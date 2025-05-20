"""
Module for creating and managing OpenSearch indices in AWS Lambda.

This module provides functionality to create OpenSearch indices with KNN vector support
through AWS Lambda functions. It handles the authentication and setup of OpenSearch
clients and index creation with specified mappings.
"""

import os
import time
import urllib
import json
import boto3
# import botocore.exceptions

from opensearchpy import (
    OpenSearch,
    RequestsHttpConnection,
    AWSV4SignerAuth,
)
from crhelper import CfnResource
from aws_lambda_powertools import Logger

logger = Logger()

helper = CfnResource(json_logging=True, log_level="INFO")

DOMAIN = os.environ["DOMAIN"]
HOST = DOMAIN.replace("https://", "")


@helper.create
def create(event, context): # pylint: disable=unused-argument
    """
    CloudFormation custom resource create handler.
    
    Args:
        event: CloudFormation custom resource event
        context: Lambda context object
    """
    logger.info("Got Create")
    index_name = event["ResourceProperties"]["IndexName"]
    logger.info("Creating index: %s", urllib.parse.quote(index_name))
    create_index(index_name)


def lambda_handler(event, context):
    """
    Main Lambda handler function.
    
    Args:
        event: Lambda event object
        context: Lambda context object
    
    Returns:
        Response from CloudFormation helper
    """
    helper(event, context)


# @tracer.capture_method(capture_response=False
def create_index(index_name: str):
    """
    Create an OpenSearch index with KNN vector support.
    
    Creates an index with the specified name and configures it with KNN vector
    mappings for vector search capabilities. Includes fields for vector data,
    text content and metadata.
    
    Args:
        index_name: Name of the index to create
        
    Raises:
        Exception: If index creation fails
    """
    try:

        region = os.environ["AWS_REGION"]

        logger.info("Sleeping for 60 seconds to give time for the access policy")
        # checkov:skip=arbitrary-sleep:Sleep is required for AWS OpenSearch Service setup to settle
        # nosemgrep: arbitrary-sleep
        time.sleep(60)

        credentials = boto3.Session().get_credentials()
        aws_auth = AWSV4SignerAuth(credentials, region, "aoss")

        logger.info("Creating the client for %s", DOMAIN)
        aoss_client = OpenSearch(
            hosts=[{"host": HOST, "port": 443}],
            http_auth=aws_auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=300,
        )

        body = {
            "settings": {"index.knn": True},
            "mappings": {
                "properties": {
                    f"{index_name}-vector": {
                        "type": "knn_vector",
                        "dimension": 1024,
                        "method": {
                            "engine": "faiss",
                            "name": "hnsw",
                            "space_type": "l2",
                        },
                    },
                    f"{index_name}-text": {"type": "text"},
                    f"{index_name}-metadata": {"type": "text", "index": False},
                }
            },
        }

        # amazonq-ignore-next-line
        logger.info("Creating index: %s", json.dumps(body))

        response = aoss_client.indices.create(index_name, body)
        logger.info("Created index: %s", response)

        logger.info("Sleeping to give time for the index to be created")
        # checkov:skip=arbitrary-sleep:Sleep is required for AWS OpenSearch Service setup to settle
        # nosemgrep: arbitrary-sleep
        time.sleep(20)
    except Exception as e:
        # nosemgrep: logging-error-without-handling
        logger.error(e)
        raise e
