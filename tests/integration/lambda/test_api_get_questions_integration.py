import os

import sys
sys.path.append('.')
sys.path.append(os.path.join(os.getcwd(), 'layers', 'pq-responder'))

from functions.api_get_questions.app import lambda_handler
from tests.mock_data.mock_lambda_context import LambdaContext
from tests.environment.environment import stack_name

class TestAPIGetQuestions():
  def test_api_get_questions(self, question_queue_name, api_question_get_last_run_parameter):
    event = {
        'startDate': '2024-01-12',
        'endDate': '2024-01-12'
      }
    context = LambdaContext({})
    os.environ['LAST_RUN_PARAMETER'] = api_question_get_last_run_parameter
    os.environ['QUESTION_QUEUE'] = question_queue_name
    os.environ['QUESTION_API_BASE_URI'] = 'https://questions-statements-api.parliament.uk/api/writtenquestions/'
    
    payload = lambda_handler(event, context)
    assert payload['statusCode'] == 200
