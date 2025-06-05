# pylint: disable=duplicate-code
"""
Lambda function that scans a Bedrock Knowledge Base.

This module handles scanning a Knowledge Base in Amazon Bedrock using the ContentBedrockKnowledgeBase client.
It is triggered by CloudWatch Alarm events and returns the scan status.

Environment Variables:
    CONTENT_KB_ID: ID of the Bedrock Knowledge Base
    CONTENT_KB_PUBLICATION_DS_ID: ID of the Knowledge Base data source
"""

import os

import botocore.exceptions

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import (
    CloudWatchAlarmEvent,
    event_source,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from repositories import ContentBedrockKnowledgeBase


logger = Logger()
tracer = Tracer()

CONTENT_KB_ID = os.environ["CONTENT_KB_ID"]
CONTENT_KB_PUBLICATION_DS_ID = os.environ["CONTENT_KB_PUBLICATION_DS_ID"]

client = ContentBedrockKnowledgeBase(kb_id=CONTENT_KB_ID)


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@event_source(data_class=CloudWatchAlarmEvent)  # pylint: disable=no-value-for-parameter
def lambda_handler(
    event: CloudWatchAlarmEvent, context: LambdaContext
):  # pylint: disable=unused-argument
    """
    Lambda handler that scans a Bedrock Knowledge Base.

    Args:
        event (CloudWatchAlarmEvent): The CloudWatch Alarm event that triggered the function
        context (LambdaContext): Lambda execution context

    Returns:
        dict: Response containing status code and optional error message
            {
                'statusCode': int,
                'body': dict (optional)
            }

    Raises:
        RuntimeError: If the knowledge base scan fails
        TypeError: If response metadata is missing
        botocore.exceptions.ClientError: If AWS API call fails
    """
    try:
        response = {}
        content_bedrock_knowledge_base = ContentBedrockKnowledgeBase(
            kb_id=CONTENT_KB_ID
        )
        response = content_bedrock_knowledge_base.sync(
            kb_ds_id=CONTENT_KB_PUBLICATION_DS_ID
        )

        if response.get("ResponseMetadata") is not None:
            if response["ResponseMetadata"]["HTTPStatusCode"] != 202:
                raise RuntimeError("Failed to scan knowledge base")
        else:
            raise TypeError(
                "Response metadata could not be retrieved due to NoneType response."
            )

        response = {
            "statusCode": 200,
        }
        return response

    except (RuntimeError, TypeError, botocore.exceptions.ClientError) as e:
        logger.error("Error: %s", e)
        return {"statusCode": 500, "body": {"message": e}}
