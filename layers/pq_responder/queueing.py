"""Module for interacting with Amazon Simple Queue Service (SQS).

This module provides a class for sending messages to SQS queues.
"""

import boto3
import botocore.exceptions

from aws_lambda_powertools import Logger

logger = Logger()

sqs_client = boto3.client("sqs")


# pylint: disable=too-few-public-methods
class SQSQueue:
    """A class to handle interactions with an Amazon SQS queue.

    Args:
        queue_name (str): The URL of the SQS queue to interact with
    """

    def __init__(self, queue_name: str):
        self.queue_name = queue_name

    def send_message(self, message: str) -> None:
        """Send a message to the SQS queue.
        
        Args:
            message (str): The message body to send to the queue
            
        Returns:
            None
        """
        logger.debug("Sending message to queue: %s", self.queue_name)

        try:
            sqs_client.send_message(QueueUrl=self.queue_name, MessageBody=message)
        except botocore.exceptions.ClientError as e:
            logger.warning("Failed to send message to queue: %s", e)
            raise e
