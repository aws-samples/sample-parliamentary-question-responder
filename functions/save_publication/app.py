"""
Lambda function handler for processing publication records from SQS.

This module receives SQS events containing publication metadata, retrieves the associated
publication files from the Parliament Publications API, and stores them in S3.
"""

import os
import json

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source

from storage import S3Storage
from models import Publication
from parliament_api_client import ParliamentPublicationsAPIClient


logger = Logger()
tracer = Tracer()

COMMITTEE_API_BASE_URI = os.environ["COMMITTEE_API_BASE_URI"]
COMMITTEE_BASE_URI = os.environ["COMMITTEE_BASE_URI"]
CONTENT_BUCKET = os.environ["CONTENT_BUCKET"]

s3_client = S3Storage(CONTENT_BUCKET)


def get_publication_file(api_base_uri: str, publication: Publication) -> bytes:
    """
    Retrieve publication file from Parliament Publications API.

    Args:
        api_base_uri (str): Base URI for the Parliament Publications API
        publication (Publication): Publication metadata object

    Returns:
        bytes: Raw publication file data
    """
    client = ParliamentPublicationsAPIClient(api_base_uri)
    file = client.get_publication_file(publication)
    return file


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@event_source(data_class=SQSEvent)  # pylint: disable=no-value-for-parameter
def lambda_handler(
    event: SQSEvent, context: LambdaContext
):  # pylint: disable=unused-argument
    """
    AWS Lambda handler for processing SQS events containing publication records.

    Processes each record in the SQS event by:
    1. Parsing the publication metadata from JSON
    2. Retrieving the publication file from the Parliament API
    3. Storing the file in S3

    Args:
        event (SQSEvent): SQS event containing publication records
        context (LambdaContext): Lambda execution context

    Returns:
        dict: Response object with status code and message

    Raises:
        JSONDecodeError: If record body contains invalid JSON
        Exception: For any other unexpected errors
    """
    try:
        for record in event.records:
            publication_json = json.loads(record.body)
            publication = Publication.from_dict(publication_json)

            file = get_publication_file(COMMITTEE_API_BASE_URI, publication)

            s3_client.save_publication(file, publication, COMMITTEE_BASE_URI)

        return {"statusCode": 200, "body": "Ok"}

    except json.JSONDecodeError as e:
        logger.error(f"JSON Decoding Error: {e}")
        return {"statusCode": 400, "body": "Invalid JSON in the request body"}
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Unexpected Error: {e}")
        return {"statusCode": 500, "body": "An unexpected error occurred"}
