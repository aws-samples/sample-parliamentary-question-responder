"""Lambda function for emptying Amazon S3 bucket in the context of a CloudFormation stack.

This module provides functionality to empty an S3 bucket when triggered by a CloudFormation
custom resource. It handles deletion of all object versions in the bucket and provides
logging of the operation.

Functions:
    delete: Handles the CloudFormation custom resource delete event
    lambda_handler: Main Lambda function handler
    empty_bucket: Empties all contents of an S3 bucket
    get_object_count: Counts objects in an S3 bucket
"""

import urllib
import boto3
import botocore.exceptions

from crhelper import CfnResource
from aws_lambda_powertools import Logger

logger = Logger()
helper = CfnResource(json_logging=True, log_level="INFO", sleep_on_delete=30)

try:
    session = boto3.Session()
except botocore.exceptions.ClientError as e:
    helper.init_failure(e)


@helper.delete
def delete(event, context): # pylint: disable=unused-argument
    """Handle CloudFormation custom resource delete event.
    
    Args:
        event: CloudFormation custom resource event
        context: Lambda context object
        
    Raises:
        Exception: If bucket emptying fails
    """
    target_bucket = event["ResourceProperties"]["TargetBucket"]
    logger.info("Target bucket: %s", urllib.parse.quote(target_bucket))
    try:
        empty_bucket(target_bucket)
    except Exception as e:
        # nosemgrep:logging-error-without-handling
        logger.error("Failed to empty bucket %s: %s", urllib.parse.quote(target_bucket), e)
        raise e


def lambda_handler(event, context):
    """Main Lambda function handler.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        Response from CfnResource helper
    """
    helper(event, context)

def empty_bucket(target_bucket):
    """Empty an S3 bucket by deleting all object versions.
    
    Args:
        target_bucket: Name of the S3 bucket to empty
        
    Raises:
        botocore.exceptions.ClientError: If deletion fails
    """
    logger.info("About to delete the files in S3 bucket %s", urllib.parse.quote(target_bucket))
    s3_resource = boto3.resource("s3")
    bucket = s3_resource.Bucket(target_bucket)

    object_count = get_object_count(bucket)
    logger.info("Found %s objects in bucket %s", object_count, urllib.parse.quote(target_bucket))

    try:
        bucket.object_versions.all().delete()
        logger.info("Deleted all object versions in bucket %s", urllib.parse.quote(target_bucket))
    except botocore.exceptions.ClientError as e:
        logger.warning(
            "Failed to delete object versions in bucket %s: %s", urllib.parse.quote(target_bucket), 
            e
        )
        raise e



def get_object_count(bucket):
    """Count the number of objects in an S3 bucket.
    
    Args:
        bucket: boto3 Bucket resource
        
    Returns:
        int: Number of objects in the bucket
    """
    object_count = 0
    for _ in bucket.objects.all():
        object_count += 1

    return object_count
