import os

from time import sleep

import pytest
import boto3
from botocore.exceptions import ClientError


@pytest.fixture(autouse=True, scope="session")
def build_environment(aws_region):
    # amazonq-ignore-next-line
    os.environ["AWS_REGION"] = aws_region


@pytest.fixture(scope="session")
def stack_outputs(aws_region, stack_name):
    """Fixture to retrieve CloudFormation stack outputs."""
    cfn_client = boto3.client("cloudformation", region_name=aws_region)
    try:
        response = cfn_client.describe_stacks(StackName=stack_name)
        if not response["Stacks"]:
            raise ValueError(f"Stack {stack_name} not found")

        # Convert the outputs into a dictionary for easier access
        outputs = {}
        for output in response["Stacks"][0]["Outputs"]:
            outputs[output["OutputKey"]] = output["OutputValue"]

        return outputs

    except cfn_client.exceptions.ClientError as e:
        raise RuntimeError(f"Error retrieving stack outputs: {str(e)}")


@pytest.fixture(scope="session")
def user_pool_id(stack_outputs):
    return stack_outputs["CognitoUserPoolId"]


@pytest.fixture(scope="session")
def user_pool_client_id(stack_outputs):
    return stack_outputs["CognitoUserPoolClientId"]


@pytest.fixture(scope="session")
def question_kb_ds_id(stack_outputs):
    return stack_outputs["QuestionKnowledgeBaseDataSourceId"]


@pytest.fixture(scope="session")
def question_kb_id(stack_outputs):
    return stack_outputs["QuestionKnowledgeBaseId"]


@pytest.fixture(scope="session")
def question_crawler_name(stack_outputs):
    return stack_outputs["QuestionCrawlerName"]


@pytest.fixture(scope="session")
def content_kb_publication_ds_id(stack_outputs):
    return stack_outputs["ContentPublicationKnowledgeBaseDataSourceId"]


@pytest.fixture(scope="session")
def content_kb_id(stack_outputs):
    return stack_outputs["ContentKnowledgeBaseId"]


@pytest.fixture(scope="session")
def populate_knowledge_base(question_bucket_name, question_kb_ds_id, question_kb_id):
    """
    Populates a knowledge base by uploading mock data to S3 and starting an ingestion job.

    Args:
        question_bucket_name (str): Name of the S3 bucket to upload mock data to
        question_kb_ds_id (str): ID of the knowledge base data source
        question_kb_id (str): ID of the knowledge base

    Raises:
        RuntimeError: If the ingestion job fails
    """
    # Copy mock data to S3 bucket
    key = "question_type=written/year=2024/month=01/day=10"
    file_name = "1681217.json"

    if not check_object_exists(question_bucket_name, os.path.join(key, file_name)):
        s3_resource = boto3.resource("s3")
        bedrock_agent_client = boto3.client("bedrock-agent")

        bucket = s3_resource.Bucket(question_bucket_name)
        file_path = os.path.join(os.getcwd(), "tests", "mock_data", "1681217.json")
        bucket.upload_file(file_path, os.path.join(key, file_name))

        # Start knowledge base ingestion job and wait to complete
        ingestion_job_id = bedrock_agent_client.start_ingestion_job(
            dataSourceId=question_kb_ds_id, knowledgeBaseId=question_kb_id
        )["ingestionJob"]["ingestionJobId"]

        while True:
            ingestion_job = bedrock_agent_client.get_ingestion_job(
                dataSourceId=question_kb_ds_id,
                ingestionJobId=ingestion_job_id,
                knowledgeBaseId=question_kb_id,
            )
            match ingestion_job["ingestionJob"]["status"]:
                case "COMPLETE":
                    break
                case "FAILED":
                    raise RuntimeError("Ingestion job failed")
                case _:
                    sleep(5)


@pytest.fixture(scope="session")
def question_bucket_name(stack_outputs):
    return stack_outputs["QuestionBucketName"]


@pytest.fixture(scope="session")
def content_bucket_name(stack_outputs):
    return stack_outputs["ContentBucketName"]


@pytest.fixture(scope="session")
def publication_queue_name(stack_outputs):
    return stack_outputs["PublicationQueueName"]


@pytest.fixture(scope="session")
def question_queue_name(stack_outputs):
    return stack_outputs["QuestionQueueName"]

@pytest.fixture(scope="session")
def api_question_get_last_run_parameter(stack_outputs):
    return stack_outputs["APIGetQuestionsLastRunParameter"]

@pytest.fixture(scope="session")
def similar_questions_flow_alias_id(stack_outputs):
    return stack_outputs["SimilarQuestionsFlowAliasId"]


@pytest.fixture(scope="session")
def similar_questions_flow_id(stack_outputs):
    return stack_outputs["SimilarQuestionsFlowId"]


@pytest.fixture(scope="session")
def site_cloudfront_url(stack_outputs):
    return stack_outputs["SiteCloudFrontUrl"]


@pytest.fixture(scope="session")
def suggest_answer_flow_id(stack_outputs):
    return stack_outputs["SuggestAnswerFlowId"]


@pytest.fixture(scope="session")
def suggest_answer_flow_alias_id(stack_outputs):
    return stack_outputs["SuggestAnswerFlowAliasId"]


@pytest.fixture(scope="session")
def suggest_answer_agent_id(stack_outputs):
    return stack_outputs["SuggestAnswerAgentId"]


@pytest.fixture(scope="session")
def suggest_answer_agent_alias_id(stack_outputs):
    return stack_outputs["SuggestAnswerAgentAliasId"]


def check_object_exists(bucket_name, object_key):
    s3_client = boto3.client("s3")
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            # Something else went wrong
            raise
