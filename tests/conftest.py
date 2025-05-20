import pytest
import json

def pytest_addoption(parser):
    parser.addoption('--awsRegion', action='store', help='AWS Region')
    parser.addoption('--stackName', action='store', help='Name of the CFN Stack')

@pytest.fixture(scope='session')
def aws_region(request):
    return request.config.getoption('--awsRegion')

@pytest.fixture(scope='session')
def stack_name(request):
    return request.config.getoption('--stackName')

@pytest.fixture
def mock_lambda_context():
    from tests.mock_data.mock_lambda_context import LambdaContext
    return LambdaContext()

@pytest.fixture()
def mock_find_similar_questions():
    from tests.mock_data.mock_find_similar_questions import MockFindSimilarQuestions
    return MockFindSimilarQuestions().mock_find_similar_questions

@pytest.fixture()
def mock_suggest_answer():
    from tests.mock_data.mock_suggest_answer import MockSuggestAnswer
    return MockSuggestAnswer().mock_suggest_answer

@pytest.fixture()
def mock_flow_build_content_kb_response():
    from tests.mock_data.mock_flow_build_content_kb_response import MockFlowBuildContentKBResponse
    return MockFlowBuildContentKBResponse().mock_flow_build_content_kb_response

@pytest.fixture()
def process_questions_event():
    with open("tests/events/process_questions.json") as f:
        return json.load(f)
    
@pytest.fixture()
def process_publications_event():
    with open("tests/events/process_publications.json") as f:
        return json.load(f)
