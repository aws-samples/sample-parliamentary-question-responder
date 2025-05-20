"""
Module for retrieving and queueing parliamentary questions.

This module provides functionality to fetch questions from a Parliament API based on date ranges
and queue them for further processing using AWS SQS. It includes error handling and logging.

The module uses Pydantic for input validation, AWS Lambda Powertools for observability,
and handles API and AWS service interactions with appropriate error handling.
"""

import os

from datetime import date, datetime

from pydantic import BaseModel, Field

import requests
import botocore.exceptions

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser

from models import Questions
from parliament_api_client import DateType, ParliamentQuestionsAPIClient
from queueing import SQSQueue
from storage import SSMStorage

logger = Logger()
tracer = Tracer()

class Event(BaseModel):
    """
    Event model for Lambda function input validation using Pydantic.

    Attributes:
        start_date (date): Start date for retrieving questions (inclusive)
        end_date (date): End date for retrieving questions (inclusive)
    """

    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")


def get_questions_by_date(
    api_base_uri: str, date_type: DateType, start_date: date, end_date: date
) -> Questions:
    """
    Retrieve parliamentary questions for a given date range from the Parliament API.

    Args:
        api_base_uri (str): Base URI for the Parliament Questions API
        date_type (DateType): Type of date to filter questions by
        start_date (date): Start date for retrieving questions (inclusive)
        end_date (date): End date for retrieving questions (inclusive)

    Returns:
        Questions: Collection of parliamentary questions matching the date criteria

    Raises:
        requests.exceptions.HTTPError: If the API request fails
    """
    client = ParliamentQuestionsAPIClient(api_base_uri)
    questions = client.get_questions_by_date(
        date_type=date_type,
        start_date=start_date,
        end_date=end_date,
    )
    return questions


def queue_questions(questions: Questions, questions_queue: str) -> None:
    """
    Queue parliamentary questions to SQS for asynchronous processing.

    Each question is serialized to JSON and sent as an individual message to the specified SQS queue.

    Args:
        questions (Questions): Collection of questions to be queued
        questions_queue (str): Name of the SQS queue to send messages to

    Raises:
        botocore.exceptions.ClientError: If there is an error sending messages to SQS
    """
    question_queue = SQSQueue(queue_name=questions_queue)
    try:
        for question in questions.questions:
            question_queue.send_message(question.model_dump_json())
    except botocore.exceptions.ClientError as e:
        logger.error(f"Error: {e}")


def update_last_run(parameter_key: str, end_date: date) -> None:
    """
    Update the last run date parameter in AWS Systems Manager Parameter Store.

    Args:
        parameter_key (str): Key of the parameter to update
        end_date (date): Date to set as the last run date

    Raises:
        botocore.exceptions.ClientError: If there is an error updating the parameter
    """
    client = SSMStorage(parameter_key=parameter_key)
    current_value = client.get_parameter()
    current_value = current_value.date() if isinstance(current_value, datetime) else current_value

    if current_value == "null" or current_value < end_date:
        client.save_parameter(end_date.strftime("%Y-%m-%d"))

@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@event_parser(model=Event)  # pylint: disable=no-value-for-parameter
def lambda_handler(
    event: Event, context: LambdaContext
):  # pylint: disable=unused-argument
    """
    AWS Lambda handler for processing parliamentary questions.

    Retrieves questions from Parliament API based on date range provided in the event
    and queues them to SQS for further processing. Uses Powertools for tracing and logging.

    Args:
        event (Event): Lambda event containing startDate and endDate dates
        context (LambdaContext): Lambda context object (unused)

    Returns:
        dict: Response containing:
            - statusCode (int): 200 for success, 500 for errors
            - body (dict): Contains either count of questions processed or error message

    Raises:
        RuntimeError: If required environment variables are missing
        botocore.exceptions.ClientError: For AWS service related errors
        requests.exceptions.HTTPError: For Parliament API request errors
    """
    try:
        question_api_base_uri = os.getenv("QUESTION_API_BASE_URI")
        question_queue = os.getenv("QUESTION_QUEUE")
        last_run_parameter = os.getenv("LAST_RUN_PARAMETER")

        if not question_api_base_uri:
            raise RuntimeError("API Base URI missing")

        if not question_queue:
            raise RuntimeError("Question Queue missing")

        if not last_run_parameter:
            raise RuntimeError("Last Run Parameter missing")

        questions = get_questions_by_date(
            api_base_uri=question_api_base_uri,
            date_type=DateType.ANSWERED,
            start_date=event.start_date,
            end_date=event.end_date,
        )
        logger.info("Retrieved %s answered questions", format(len(questions.questions)))

        queue_questions(questions=questions, questions_queue=question_queue)

        update_last_run(parameter_key=last_run_parameter, end_date=event.end_date)

        return {"statusCode": 200, "body": {"Count": len(questions.questions)}}

    except (
        RuntimeError,
        botocore.exceptions.ClientError,
        requests.exceptions.HTTPError,
    ) as e:
        logger.error("Error: %s", e)
        return {"statusCode": 500, "body": {"message": e}}
