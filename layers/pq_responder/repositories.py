"""
This module provides classes for interacting with Amazon Bedrock services including Agents,
Knowledge Bases, and Flows. It handles communication with Bedrock APIs for tasks like
question answering, similarity search, and content retrieval.
"""

import json
import random
import time
import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from aws_lambda_powertools import Logger, Metrics

from models import Questions, Question

logger = Logger()
metrics = Metrics()

config = Config(retries={"max_attempts": 5, "mode": "adaptive"})

bedrock_agent_client = boto3.client("bedrock-agent")
bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime", config=config)
s3_client = boto3.client("s3")
glue_client = boto3.client("glue")


# pylint: disable=too-few-public-methods
class BedrockAgent:
    """
    Class for interacting with Amazon Bedrock Agents.

    Attributes:
        agent_id (str): The ID of the Bedrock agent
        agent_alias_id (str): The alias ID of the Bedrock agent
    """

    def __init__(self, agent_id: str, agent_alias_id: str):
        """
        Initialize BedrockAgent with agent and alias IDs.

        Args:
            agent_id (str): The ID of the Bedrock agent
            agent_alias_id (str): The alias ID of the Bedrock agent
        """
        self.agent_id = agent_id
        self.agent_alias_id = agent_alias_id

    def suggest_answer(self, prompt: str, session_id: str = None) -> dict:
        """
        Get an answer suggestion from the Bedrock agent for a given prompt.

        Args:
            prompt (str): The input text prompt
            session_id (str, optional): Session ID for the conversation. Defaults to None.

        Returns:
            dict: Response containing completion text and session ID

        Raises:
            ClientError: If the agent invocation fails after retries
        """
        logger.debug(f"Suggesting answer to: {prompt}")

        if session_id is None:
            session_id = str(uuid.uuid4())

        max_retries = 10
        base_delay = 1
        
        for attempt in range(max_retries + 1):
            try:
                response = bedrock_agent_runtime_client.invoke_agent(
                    agentId=self.agent_id,
                    agentAliasId=self.agent_alias_id,
                    inputText=prompt,
                    sessionId=session_id,
                )

                completion = ""
                for event in response.get("completion"):
                    chunk = event["chunk"]
                    completion = completion + chunk["bytes"].decode()

                return {
                    "completion": completion,
                    "sessionId": session_id,
                }

            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'throttlingException' and attempt < max_retries:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"ThrottlingException on attempt {attempt + 1}, retrying in {delay:.2f}s")
                    time.sleep(delay)
                    continue
                
                logger.warning("Couldn't invoke agent, %s", e)
                raise e
        
        return None


# pylint: disable=too-few-public-methods
class BedrockFlow:
    """
    Class for interacting with Amazon Bedrock Flows.

    Attributes:
        flow_alias_identifier (str): The alias identifier for the flow
        flow_identifier (str): The identifier for the flow
    """

    def __init__(self, flow_alias_identifier: str, flow_identifier: str):
        """
        Initialize BedrockFlow with flow identifiers.

        Args:
            flow_alias_identifier (str): The alias identifier for the flow
            flow_identifier (str): The identifier for the flow
        """
        self.flow_alias_identifier = flow_alias_identifier
        self.flow_identifier = flow_identifier

    # pylint: disable=inconsistent-return-statements
    def find_similar_questions(self, question: str) -> Questions:
        """
        Find questions similar to the input question using the Bedrock flow.

        Args:
            question (str): The question to find similar questions for

        Returns:
            Questions: Collection of similar questions found

        Raises:
            JSONDecodeError: If response parsing fails
            Exception: For other errors during processing
        """
        logger.debug(f"Finding similar questions to: {question}")

        response = bedrock_agent_runtime_client.invoke_flow(
            # enableTrace=False,
            flowAliasIdentifier=self.flow_alias_identifier,
            flowIdentifier=self.flow_identifier,
            inputs=[
                {
                    "content": {"document": question},
                    "nodeName": "Start",
                    "nodeOutputName": "document",
                }
            ],
        )

        result = {}

        for event in response.get("responseStream"):
            result.update(event)

        if result["flowCompletionEvent"]["completionReason"] == "SUCCESS":
            result_content = result["flowOutputEvent"]["content"]["document"]
            try:
                questions = Questions()

                for item in result_content:
                    bucket_name = item["location"]["s3Location"]["uri"].split("/")[2]
                    key_elements = item["location"]["s3Location"]["uri"].split("/")[3:]
                    key = "/".join(key_elements)
                    s3_response = s3_client.get_object(Bucket=bucket_name, Key=key)
                    content = s3_response["Body"].read().decode("utf-8")
                    question = Question.from_dict(json.loads(content))
                    questions.add(question)

            except json.JSONDecodeError as e:
                logger.error("JSONDecodeError:", e)
                raise e
            except Exception as e:
                logger.error("An error occurred:", e)
                raise e

            return questions
        logger.error(
            "The prompt flow invocation didn't complete successfully because of the following reason:",
            result["flowCompletionEvent"]["completionReason"],
        )


# pylint: disable=too-few-public-methods
class BedrockKnowledgeBase:
    """
    Base class for interacting with Amazon Bedrock Knowledge Bases.

    Attributes:
        kb_id (str): The ID of the knowledge base
    """

    def __init__(self, kb_id: str):
        """
        Initialize BedrockKnowledgeBase with knowledge base ID.

        Args:
            kb_id (str): The ID of the knowledge base
        """
        self.kb_id = kb_id

    def sync(self, kb_ds_id: str):
        """
        Start an ingestion job for the knowledge base.

        Args:
            kb_ds_id (str): The data source ID for the knowledge base

        Returns:
            dict: Response from the ingestion job start request
        """
        logger.info(f"Scanning {kb_ds_id}")

        response = bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=self.kb_id, dataSourceId=kb_ds_id
        )

        return response


# pylint: disable=too-few-public-methods
class QuestionBedrockKnowledgeBase(BedrockKnowledgeBase):
    """
    Class for handling question-specific knowledge base operations.
    Inherits from BedrockKnowledgeBase.
    """


# pylint: disable=too-few-public-methods
class ContentBedrockKnowledgeBase(BedrockKnowledgeBase):
    """
    Class for content-specific knowledge base operations.
    Inherits from BedrockKnowledgeBase.
    """

    def retrieve(self, question: str) -> dict:
        """
        Retrieve content from the knowledge base based on a question.

        Args:
            question (str): The question to retrieve content for

        Returns:
            dict: Retrieved content and metadata
        """
        response = bedrock_agent_runtime_client.retrieve(
            retrievalQuery={"text": question},
            knowledgeBaseId=self.kb_id,
            retrievalConfiguration={
                "vectorSearchConfiguration": {"overrideSearchType": "HYBRID"}
            },
        )

        # Update the response metadata to point to the original URI
        for item in response["retrievalResults"]:
            if "canonicalURL" in item["metadata"]:
                item["location"]["type"] = "WEB"
                item["location"].setdefault("webLocation", {})["uri"] = item[
                    "metadata"
                ]["canonicalURL"]
                item["location"].pop("s3Location", None)

        return response


class GlueCrawler:
    """
    Class for managing AWS Glue crawlers.

    Attributes:
        crawler_name (str): The name of the Glue crawler
    """

    def __init__(self, crawler_name: str):
        """
        Initialize GlueCrawler with crawler name.

        Args:
            crawler_name (str): The name of the Glue crawler
        """
        self.crawler_name = crawler_name

    def run(self):
        """
        Start the Glue crawler.

        Returns:
            dict: Response from the crawler start request
        """
        logger.info(f"Running {self.crawler_name}")

        response = glue_client.start_crawler(Name=self.crawler_name)

        return response
