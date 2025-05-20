"""
AWS Lambda function for suggesting answers using Amazon Bedrock Agent.

This module provides an API endpoint that accepts prompts and returns suggested answers
using a Bedrock Agent. It includes request validation, error handling, and logging.
"""

import os
import json

from pydantic import BaseModel

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types
from aws_lambda_powertools.event_handler.openapi.exceptions import RequestValidationError
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from repositories import BedrockAgent

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver(enable_validation=True)

SUGGEST_ANSWER_AGENT_ALIAS_ID = os.environ["SUGGEST_ANSWER_AGENT_ALIAS_ID"]
SUGGEST_ANSWER_AGENT_ID = os.environ["SUGGEST_ANSWER_AGENT_ID"]

class Prompt(BaseModel):
    """
    Request model for prompt data.

    Attributes:
        prompt (str): The input prompt text to generate a suggested answer for
    """
    prompt: str

@app.exception_handler(RequestValidationError)
def handle_validation_error(ex: RequestValidationError):
    """
    Handle validation errors for API requests.

    Args:
        ex (RequestValidationError): The validation error that occurred

    Returns:
        Response: HTTP 422 response with error message
    """
    logger.error("Request failed validation", path=app.current_event.path, errors=ex.errors())

    return Response(
        status_code=422,
        content_type=content_types.APPLICATION_JSON,
        body="Invalid data",
    )

@tracer.capture_lambda_handler
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    AWS Lambda handler function.

    Args:
        event (dict): Lambda event data
        context (LambdaContext): Lambda context object

    Returns:
        dict: API Gateway response
    """
    return app.resolve(event, context)

@app.post("/api/suggest-answer")
@tracer.capture_method
def suggest_answer(body: Prompt, session_id: str = None) -> str:
    """
    Generate a suggested answer for the given prompt using Bedrock Agent.

    Args:
        body (Prompt): Request body containing the prompt
        session_id (str, optional): Session ID for maintaining context

    Returns:
        str: JSON string containing the suggested answer

    Raises:
        Exception: If answer generation fails
    """
    try:
        bedrock_agent = BedrockAgent(
            agent_id=SUGGEST_ANSWER_AGENT_ID,
            agent_alias_id=SUGGEST_ANSWER_AGENT_ALIAS_ID,
        )

        suggested_answer = bedrock_agent.suggest_answer(prompt=body.prompt, session_id=session_id)

        return json.dumps(suggested_answer)

    except Exception as e:
        logger.warning(e)
        raise e
