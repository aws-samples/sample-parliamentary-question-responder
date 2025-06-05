# pylint: disable=duplicate-code
"""
Module for retrieving and queueing parliamentary questions.

This module provides functionality to fetch answered questions from a Parliament API based on schedule
and queue them for further processing using AWS SQS. It includes error handling and logging.

The module uses Pydantic for input validation, AWS Lambda Powertools for observability,
and handles API and AWS service interactions with appropriate error handling.
"""

import os

from datetime import date, datetime, timedelta

import requests
import botocore.exceptions

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from models import Questions
from parliament_api_client import DateType, ParliamentQuestionsAPIClient
from queueing import SQSQueue
from storage import SSMStorage

logger = Logger()
tracer = Tracer()

def get_questions_by_date(
    api_base_uri: str, date_type: DateType, start_date: date, end_date: date
) -> Questions:
    """
    Retrieve parliamentary questions for a given date range from the Parliament API.

    Args:
        api_base_uri (str): Base URI for the Parliament Questions API
        date_type (DateType): Type of date to filter questions by (e.g. ANSWERED)
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
    Logs an error if sending to SQS fails but does not re-raise the exception.

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


def update_last_run(ssm_client: SSMStorage, end_date: date) -> None:
    """
    Update the last run date parameter in AWS Systems Manager Parameter Store.
    Only updates if the current value is "null" or less than the new end date.

    Args:
        ssm_client (SSMStorage): SSM client instance to interact with Parameter Store
        end_date (date): Date to set as the last run date

    Raises:
        botocore.exceptions.ClientError: If there is an error updating the parameter
    """
    current_value = ssm_client.get_parameter()
    current_value = current_value.date() if isinstance(current_value, datetime) else current_value
    if current_value == "null" or current_value < end_date:
        ssm_client.save_parameter(end_date.strftime("%Y-%m-%d"))

@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def lambda_handler(
    event: dict, context: LambdaContext
):  # pylint: disable=unused-argument
    """
    AWS Lambda handler for processing parliamentary questions.

    Retrieves answered questions from Parliament API based on the last run date stored in SSM Parameter Store
    up to the current date, and queues them to SQS for further processing. Uses Powertools for 
    tracing and logging. If no last run date exists, defaults to looking back a configurable number of days.

    Required environment variables:
        - QUESTION_API_BASE_URI: Base URI for the Parliament Questions API
        - QUESTION_QUEUE: Name of the SQS queue for questions
        - LAST_RUN_PARAMETER: Name of the SSM parameter storing last run date
        - DEFAULT_DAYS_TO_RETRIEVE: Number of days to look back if no last run date

    Args:
        event (dict): Lambda event (not used in current implementation)
        context (LambdaContext): Lambda context object (unused)

    Returns:
        dict: Response containing:
            - statusCode (int): 200 for success, 500 for errors
            - body (dict): Contains either count of questions processed or error message string

    Raises:
        RuntimeError: If required environment variables are missing
        botocore.exceptions.ClientError: For AWS service related errors
        requests.exceptions.HTTPError: For Parliament API request errors
    """
    try:
        question_api_base_uri = os.getenv("QUESTION_API_BASE_URI")
        question_queue = os.getenv("QUESTION_QUEUE")
        last_run_parameter = os.getenv("LAST_RUN_PARAMETER")
        default_days_to_retrieve = os.getenv("DEFAULT_DAYS_TO_RETRIEVE")

        if not question_api_base_uri:
            raise RuntimeError("API Base URI missing")

        if not question_queue:
            raise RuntimeError("Question Queue missing")

        if not last_run_parameter:
            raise RuntimeError("Last Run Parameter missing")

        if not default_days_to_retrieve:
            raise RuntimeError("Default Days to Retrieve missing")

        ssm_client = SSMStorage(parameter_key=last_run_parameter)
        last_run = ssm_client.get_parameter()
        if last_run == "null":
            last_run = date.today() - timedelta(days=int(default_days_to_retrieve))
        else:
            last_run = last_run.date() if isinstance(last_run, datetime) else last_run

        end_date = date.today()

        questions = get_questions_by_date(
            api_base_uri=question_api_base_uri,
            date_type=DateType.ANSWERED,
            start_date=last_run,
            end_date=end_date,
        )
        logger.info("Retrieved %s answered questions", format(len(questions.questions)))

        queue_questions(questions=questions, questions_queue=question_queue)

        update_last_run(ssm_client, end_date=end_date)

        return {"statusCode": 200, "body": {"Count": len(questions.questions)}}

    except (
        RuntimeError,
        botocore.exceptions.ClientError,
        requests.exceptions.HTTPError,
    ) as e:
        logger.error("Error: %s", e)
        return {"statusCode": 500, "body": {"message": e}}
