"""
Module for handling storage of questions and publications in Amazon S3 and parameters in SSM.

This module provides the S3Storage class which handles saving question and publication 
objects to S3, including their associated metadata, and the SSMStorage class for storing
parameters in SSM Parameter Store. It uses boto3 for AWS operations and includes logging 
and metrics via AWS Lambda Powertools.
"""

import json
import boto3
import boto3.exceptions
import botocore.exceptions

from datetime import datetime
from aws_lambda_powertools import Logger, Metrics

from models import Question, Publication

logger = Logger()
metrics = Metrics()

s3_client = boto3.client("s3")
ssm_client = boto3.client("ssm")


class SSMStorage:
    """Class for handling storage of parameters in SSM Parameter Store."""

    def __init__(self, parameter_key: str):
        """Initialize SSMStorage with parameter key.

        Args:
            parameter_key (str): Key name for the SSM parameter
        """
        self.ssm_parameter_key = parameter_key

    def save_parameter(self, parameter_value: str):
        """Save a parameter value to SSM Parameter Store.

        Args:
            parameter_value (str): Value to save in SSM

        Raises:
            botocore.exceptions.ClientError: If saving to SSM fails
        """
        try:
            ssm_client.put_parameter(
                Name=self.ssm_parameter_key,
                Value=parameter_value,
                Type="String",
                Overwrite=True,
            )
        except botocore.exceptions.ClientError as e:
            logger.warning("Failed to save parameter to SSM: %s", e)
            raise e
        
    def get_parameter(self) -> datetime:
        """Retrieve a parameter value from SSM Parameter Store.

        Returns:
            datetime: Parsed datetime from parameter value, or "null" if value is "null"

        Raises:
            botocore.exceptions.ClientError: If retrieving from SSM fails
        """
        try:
            response = ssm_client.get_parameter(Name=self.ssm_parameter_key)
        except botocore.exceptions.ClientError as e:
            logger.warning("Failed to retrieve parameter from SSM: %s", e)
            raise e

        if response["Parameter"]["Value"] == "null":
            return "null"
        
        return datetime.strptime(response["Parameter"]["Value"], "%Y-%m-%d")

class S3Storage:
    """Class for handling storage of questions and publications in S3."""

    def __init__(self, bucket_name):
        """Initialize S3Storage with bucket name.

        Args:
            bucket_name (str): Name of the S3 bucket to use for storage
        """
        self.bucket_name = bucket_name

    def save_question(self, question: Question):
        """Save a question object to S3 in JSON format.

        The question is saved with a key following the pattern:
        question_type=written/year=YYYY/month=MM/day=DD/question_id.json

        Args:
            question (Question): Question object to save

        Returns:
            str: ID of the saved question

        Raises:
            boto3.exceptions.S3UploadFailedError: If upload to S3 fails or response is invalid
        """
        key = f"question_type=written/year={question.date_tabled.year:04d}/month={question.date_tabled.month:02d}/day={question.date_tabled.day:02d}/{question.id}.json"
        logger.debug("Saving %s to S3", key)
        metrics.add_metric(name="QuestionSaveS3", unit="Count", value=1)

        response = s3_client.put_object(
            Body=question.model_dump_json(), Bucket=self.bucket_name, Key=key
        )

        if (
            not (response.get("ResponseMetadata"))
            or response["ResponseMetadata"]["HTTPStatusCode"] != 200
        ):
            raise boto3.exceptions.S3UploadFailedError

        return question.id

    def save_publication(self, file: dict, publication: Publication, web_base_uri: str):
        """Save a publication file and its metadata to S3.

        Saves both the publication file and a separate metadata JSON file with the same key
        plus '.metadata.json' suffix. The files are saved under a key following the pattern:
        document_type=publication/committee_id=<id>/<filename>

        Args:
            file (dict): Dictionary containing publication file data in 'data' key
            publication (Publication): Publication object containing metadata
            web_base_uri (str): Base URI for constructing canonical URLs

        Returns:
            dict: Response from S3 put_object operation for metadata file

        Raises:
            botocore.exceptions.ClientError: If upload of either file or metadata to S3 fails
        """
        try:
            file_content = file["data"]
            committee_id = publication.committee_id
            file_name = publication.documents[0].files[0].filename
            object_key = f"document_type=publication/committee_id={str(committee_id)}/{file_name}"
            response = s3_client.put_object(
                Bucket=self.bucket_name, Key=object_key, Body=file_content
            )
        except botocore.exceptions.ClientError as e:
            logger.warning("Failed to save publication to S3: %s", e)
            raise e

        try:
            metadata = self.build_publication_metadata(publication, web_base_uri)
            response = s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"{object_key}.metadata.json",
                Body=json.dumps(metadata),
            )
        except botocore.exceptions.ClientError as e:
            logger.warning("Failed to save publication metadata to S3: %s", e)
            raise e

        return response

    def build_publication_metadata(
        self, publication: Publication, web_base_uri: str
    ) -> dict:
        """Build metadata dictionary for a publication.

        Creates a metadata dictionary containing the committee ID and canonical URL,
        formatted for S3 storage with embedding flags.

        Args:
            publication (Publication): Publication object to build metadata for
            web_base_uri (str): Base URI for constructing canonical URLs

        Returns:
            dict: Metadata dictionary with committee ID and canonical URL attributes
                 in the format required for S3 storage with embedding flags
        """
        url = f"{web_base_uri}{publication.documents[0].web_uri_path}"

        metadata = {
            "metadataAttributes": {
                "committeeId": {
                    "value": {
                        "type": "NUMBER",
                        "numberValue": publication.committee_id,
                    },
                    "includeForEmbedding": True,
                },
                "canonicalURL": {
                    "value": {"type": "STRING", "stringValue": url},
                    "includeForEmbedding": True,
                },
            }
        }

        return metadata
