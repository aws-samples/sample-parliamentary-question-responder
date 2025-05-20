"""
This module provides an AWS Lambda function that handles API Gateway requests for finding similar questions
using Amazon Bedrock Flow. It exposes a REST endpoint that accepts a question and returns similar questions
using the Bedrock Flow service.
"""

import os

from typing_extensions import Annotated

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from models import Questions
from repositories import BedrockFlow

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver(enable_validation=True)

SIMILAR_QUESTIONS_FLOW_ALIAS_ID = os.environ['SIMILAR_QUESTIONS_FLOW_ALIAS_ID']
SIMILAR_QUESTIONS_FLOW_ID = os.environ['SIMILAR_QUESTIONS_FLOW_ID']

@tracer.capture_lambda_handler
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    AWS Lambda handler function that processes API Gateway events.
    
    Args:
        event (dict): The AWS Lambda event object containing API Gateway event data
        context (LambdaContext): The AWS Lambda context object
        
    Returns:
        dict: The API Gateway response
    """
    return app.resolve(event, context)

@app.get('/api/similar-questions')
@tracer.capture_method
def get_similar_questions(question: Annotated[str, Query(min_length=5)]) -> Questions:
    """
    Endpoint handler that finds similar questions using Bedrock Flow.
    
    Args:
        question (str): The input question to find similar questions for. 
                       Must be at least 5 characters long.
        
    Returns:
        Questions: A collection of similar questions found by Bedrock Flow
        
    Raises:
        Exception: If there is an error processing the request
    """
    try:
        bedrock_flow = BedrockFlow(
            flow_alias_identifier=SIMILAR_QUESTIONS_FLOW_ALIAS_ID,
            flow_identifier=SIMILAR_QUESTIONS_FLOW_ID
        )

        similar_questions: Questions = bedrock_flow.find_similar_questions(question=question)

        return similar_questions
    except Exception as e:
        logger.warning(e)
        raise e
