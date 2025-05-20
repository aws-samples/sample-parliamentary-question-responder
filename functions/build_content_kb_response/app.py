"""
Lambda function handler for processing Bedrock Agent events.
Retrieves responses from a Content Knowledge Base based on input questions.

This module integrates with AWS Bedrock Agent to handle question-answer interactions
using a configured knowledge base.
"""

import os
import json

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import event_source, BedrockAgentEvent

from repositories import ContentBedrockKnowledgeBase

logger = Logger()
tracer = Tracer()

CONTENT_KB_ID = os.environ["CONTENT_KB_ID"]

client = ContentBedrockKnowledgeBase(kb_id=CONTENT_KB_ID)


@event_source(data_class=BedrockAgentEvent) # pylint: disable=no-value-for-parameter
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: BedrockAgentEvent, context: LambdaContext): # pylint: disable=unused-argument
    """
    Process Bedrock Agent events and return responses from the knowledge base.

    Args:
        event (BedrockAgentEvent): The event received from Bedrock Agent containing the question
        context (LambdaContext): Lambda execution context

    Returns:
        dict: Response containing the knowledge base answer formatted for Bedrock Agent

    Raises:
        Exception: If question retrieval fails
    """
    try:
        for parameter in event.parameters:
            if parameter["name"] == "Question":
                question = parameter["value"]
                break

        logger.debug(f"Question: {question}")
        response = client.retrieve(question)
        logger.debug(f"Response: {response}")

        response_body = {
            'TEXT': {
                'body': json.dumps(response)
            }
        }

        function_response = {
            'actionGroup': event.action_group,
            'function': "BuildContentKBResponse",
            'functionResponse': {
                "responseBody": response_body
            }
        }

        action_response = {
            "messageVersion": "1.0",
            "response": function_response,
        }

        logger.debug("Action Response: %s", action_response)
        return action_response

    except Exception as e:
        # nosemgrep: logging-error-without-handling
        logger.error("Failed to retrieve question: %s", e)
        raise
