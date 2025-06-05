# pylint: disable=duplicate-code
"""
Lambda function that handles CloudWatch alarm events to scan a Bedrock knowledge base and run a Glue crawler.

This module contains functionality to:
1. Sync a Bedrock knowledge base using provided KB ID and dataset ID
2. Run a Glue crawler to process the knowledge base data
"""

import os

import botocore.exceptions

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import (
    CloudWatchAlarmEvent,
    event_source,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from repositories import QuestionBedrockKnowledgeBase, GlueCrawler


logger = Logger()
tracer = Tracer()

QUESTIONS_KB_ID = os.environ["QUESTIONS_KB_ID"]
QUESTIONS_KB_DS_ID = os.environ["QUESTIONS_KB_DS_ID"]

CRAWLER_NAME = os.environ["CRAWLER_NAME"]

client = QuestionBedrockKnowledgeBase(kb_id=QUESTIONS_KB_ID)


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@event_source(data_class=CloudWatchAlarmEvent) # pylint: disable=no-value-for-parameter
def lambda_handler(event: CloudWatchAlarmEvent, context: LambdaContext): # pylint: disable=unused-argument
    """
    AWS Lambda handler function that processes CloudWatch alarm events.
    
    Args:
        event (CloudWatchAlarmEvent): The CloudWatch alarm event trigger
        context (LambdaContext): Lambda execution context
        
    Returns:
        dict: Response object containing status code and optional error message
        
    Raises:
        RuntimeError: If scanning knowledge base or starting crawler fails
        TypeError: If response metadata is missing
        botocore.exceptions.ClientError: For AWS API errors
    """
    try:
        response = {}
        question_bedrock_knowledge_base = QuestionBedrockKnowledgeBase(
            kb_id=QUESTIONS_KB_ID
        )
        response = question_bedrock_knowledge_base.sync(kb_ds_id=QUESTIONS_KB_DS_ID)

        if response.get("ResponseMetadata") is not None:
            if response["ResponseMetadata"]["HTTPStatusCode"] != 202:
                raise RuntimeError("Failed to scan knowledge base")
            logger.info("Successfully scanned knowledge base")
        else:
            raise TypeError(
                "Response metadata could not be retrieved due to NoneType response."
            )

        question_crawler = GlueCrawler(CRAWLER_NAME)
        response = question_crawler.run()
        if response.get("ResponseMetadata") is not None:
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise RuntimeError("Failed to start crawler knowledge base")
            logger.info("Successfully started crawler")
        else:
            raise TypeError(
                "Response metadata could not be retrieved due to NoneType response."
            )

        response = {
            "statusCode": 200,
        }

        return response

    except (RuntimeError, TypeError, botocore.exceptions.ClientError) as e:
        logger.error("Error: %s" , e)
        return {"statusCode": 500, "body": {"message": e}}
