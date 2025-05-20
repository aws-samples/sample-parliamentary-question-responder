"""
Lambda function to retrieve committee publications from Parliament API and 
queue them for processing.

This module handles fetching publications for a specified committee within a date range
and queuing them to an SQS queue for further processing.
"""

import os

from datetime import date

import botocore.exceptions

from pydantic import BaseModel, Field

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser

from models import Publications
from parliament_api_client import ParliamentPublicationsAPIClient
from queueing import SQSQueue


logger = Logger()
tracer = Tracer()

COMMITTEE_API_BASE_URI = os.environ["COMMITTEE_API_BASE_URI"]
PUBLICATION_QUEUE = os.environ["PUBLICATION_QUEUE"]


class Event(BaseModel):
    """
    Event model for Lambda input parameters.

    Attributes:
        committee_id: ID of the committee to fetch publications for
        start_date: Start date of the date range to fetch publications
        end_date: End date of the date range to fetch publications
    """

    committee_id: int = Field(alias="committeeId")
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")


def get_committee_publications_list(
    api_base_uri: str, committee_id: int, start_date: date, end_date: date
) -> list:
    """
    Fetch committee publications from the Parliament API.

    Args:
        api_base_uri: Base URI for the Parliament API
        committee_id: ID of the committee to fetch publications for
        start_date: Start date of the date range
        end_date: End date of the date range

    Returns:
        List of publications for the specified committee and date range
    """
    client = ParliamentPublicationsAPIClient(api_base_uri)
    publications = client.get_committee_publications_list(
        committee_id=committee_id, start_date=start_date, end_date=end_date
    )
    return publications


def queue_publications(publications: Publications, publication_queue: str) -> None:
    """
    Queue publications to SQS for processing.

    Args:
        publications: Publications object containing list of publications to queue
        publication_queue: Name of the SQS queue to send messages to

    Raises:
        botocore.exceptions.ClientError: If there is an error sending messages to SQS
    """
    publication_queue = SQSQueue(queue_name=publication_queue)
    try:
        for publication in publications.publications:
            publication_queue.send_message(publication.model_dump_json())
    except botocore.exceptions.ClientError as e:
        logger.error("Error: %s", e)


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@event_parser(model=Event)  # pylint: disable=no-value-for-parameter
def lambda_handler(
    event: Event, context: LambdaContext  # pylint: disable=unused-argument
) -> dict:
    """
    Lambda handler to process committee publications.

    Args:
        event: Lambda event containing committee ID and date range
        context: Lambda context object

    Returns:
        Dictionary containing status code and count of publications processed

    Raises:
        RuntimeError: If required environment variables are missing
        botocore.exceptions.ClientError: If there is an error with AWS services
    """
    try:
        api_base_uri = COMMITTEE_API_BASE_URI
        if not api_base_uri:
            raise RuntimeError("API Base URI missing")
        question_queue = PUBLICATION_QUEUE
        if not question_queue:
            raise RuntimeError("Question Queue missing")

        publications = get_committee_publications_list(
            api_base_uri=api_base_uri,
            committee_id=event.committee_id,
            start_date=event.start_date,
            end_date=event.end_date,
        )
        queue_publications(publications, question_queue)

        return {"statusCode": 200, "body": {"Count": len(publications.publications)}}
    except (RuntimeError, botocore.exceptions.ClientError) as e:
        logger.error("Error: %s", e)
        return {"statusCode": 500, "body": {"message": e}}
