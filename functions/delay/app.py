"""Lambda function for sleeping for a specified duration in the context of a CloudFormation stack.

This module provides functionality to sleep for a specified number of seconds when triggered by a CloudFormation
custom resource. It handles the sleep operation and provides logging.

Functions:
    create: Handles the CloudFormation custom resource create event
    lambda_handler: Main Lambda function handler
"""
from time import sleep
from crhelper import CfnResource
from aws_lambda_powertools import Logger

logger = Logger()
helper = CfnResource(json_logging=True, log_level="INFO", sleep_on_delete=30)


@helper.create
@helper.update
def create(event, context): # pylint: disable=unused-argument
    """Handle CloudFormation custom resource create event.
    
    Args:
        event: CloudFormation custom resource event containing SleepSeconds property
        context: Lambda context object
        
    Returns:
        None
    """
    sleep_seconds = event["ResourceProperties"]["SleepSeconds"]
    logger.info("Sleeping for : %s", sleep_seconds)

    sleep(int(sleep_seconds))

def lambda_handler(event, context):
    """Main Lambda function handler.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        Response from CfnResource helper
    """
    helper(event, context)
