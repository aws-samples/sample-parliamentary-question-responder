"""
This module processes parliamentary questions from an SQS queue and saves them to S3.
It retrieves full question details from the Parliament Questions API and handles storage operations.
"""

import os
import json
from dateutil import parser
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source

from storage import S3Storage
from parliament_api_client import ParliamentQuestionsAPIClient
from models import Question, House

logger = Logger()
tracer = Tracer()

QUESTION_API_BASE_URI = os.environ["QUESTION_API_BASE_URI"]
QUESTIONS_BUCKET = os.environ["QUESTIONS_BUCKET"]


def save_question(question: Question, questions_bucket: str) -> None:
    """
    Save a parliamentary question to S3 storage.

    Args:
        question (Question): The question object to save
        questions_bucket (str): Name of the S3 bucket to save to

    Returns:
        None
    """
    question_repository = S3Storage(bucket_name=questions_bucket)
    question_repository.save_question(question)


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@event_source(data_class=SQSEvent)  # pylint: disable=no-value-for-parameter
def lambda_handler(
    event: SQSEvent, context: LambdaContext
):  # pylint: disable=unused-argument
    """
    AWS Lambda handler that processes SQS events containing parliamentary questions.

    Retrieves questions from SQS, gets full details from Parliament API, and saves to S3.

    Args:
        event (SQSEvent): The SQS event containing question data
        context (LambdaContext): Lambda execution context

    Returns:
        dict: Response object with status code and body
    """
    try:
        parliament_api_client = ParliamentQuestionsAPIClient(
            base_uri=QUESTION_API_BASE_URI
        )

        for record in event.records:
            json_question = json.loads(record.body)
            logger.debug(f"Question: {json_question}")
            question = Question(
                id=json_question["id"],
                house=House(json_question["house"].lower()),
                date_tabled=parser.parse(json_question["date_tabled"]),
                question=json_question["question"],
                answer=json_question["answer"],
            )

            full_question = parliament_api_client.get_full_question(question)
            save_question(full_question, QUESTIONS_BUCKET)

        return {"statusCode": 200, "body": "Ok"}

    except json.JSONDecodeError as json_error:
        logger.error(f"JSON Decoding Error: {json_error}")
        return {"statusCode": 400, "body": "Invalid JSON in the request body"}
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error: %s", e)
        return {"statusCode": 500, "body": {"message": e}}
