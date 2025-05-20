import pytest
import os 

import boto3

from moto import mock_aws

@pytest.fixture()
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    # amazonq-ignore-next-line
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing" # pragma: allowlist secret # nosec
    os.environ["AWS_SECURITY_TOKEN"] = "testing" # nosec
    os.environ["AWS_SESSION_TOKEN"] = "testing" # nosec

@pytest.fixture()
def s3_client(aws_credentials):
    with mock_aws():
        yield boto3.client("s3")

@pytest.fixture()
def ssm_client(aws_credentials):
    with mock_aws():
        yield boto3.client("ssm")

@pytest.fixture()
def sqs_client(aws_credentials):
    with mock_aws():
        yield boto3.client("sqs")

@pytest.fixture
def mock_education_committee_id():
    return 203

@pytest.fixture()
def mock_parliament_committees_api_uri():
    parliament_api_base_uri = 'https://example.com/api/'
    os.environ['API_BASE_URI'] = parliament_api_base_uri

    return parliament_api_base_uri

@pytest.fixture()
def mock_parliament_questions_api_uri():
    parliament_api_base_uri = 'https://example.com/api/writtenquestions/'
    os.environ['QUESTION_API_BASE_URI'] = parliament_api_base_uri

    return parliament_api_base_uri

@pytest.fixture()
def mock_api_question():
    from tests.mock_data.mock_api_question import MockAPIQuestion
    yield MockAPIQuestion().mock_api_question

@pytest.fixture()
def mock_api_questions():
    from tests.mock_data.mock_api_questions import MockAPIQuestions
    yield MockAPIQuestions().mock_api_questions


@pytest.fixture()
def create_last_run_parameter(ssm_client, aws_region, stack_name):
    parameter_name = f"{stack_name}-QuestionsAPIGetQuestionsLastRun"
    ssm_client.put_parameter(
        Name=parameter_name,
        Value='null',
        Type='String'
    )
    os.environ['LAST_RUN_PARAMETER'] = parameter_name

@pytest.fixture()
def create_question_s3_bucket(s3_client, aws_region):
    bucket_name = 'questions_bucket'
    response = s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': aws_region
        }
    )
    if response.get('ResponseMetadata'):
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RuntimeError('Error creating bucket')
    else:
        raise RuntimeError('Error creating bucket')
    os.environ['QUESTIONS_BUCKET'] = bucket_name

