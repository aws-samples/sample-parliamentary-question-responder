import pytest
import json
import os
import sys
import requests

sys.path.append('.')
sys.path.append(os.path.join(os.getcwd(), 'layers', 'pq_responder'))

from unittest.mock import patch, MagicMock
# from moto import mock_sqs

from functions.api_get_questions.app import lambda_handler

class TestAPIGetQuestions:

    @pytest.fixture()
    def create_sqs_queue(self, sqs_client):
        sqs_queue = sqs_client.create_queue(QueueName='QuestionQueue')
        os.environ['QUESTION_QUEUE'] = sqs_queue['QueueUrl']

    @patch('parliament_api_client.requests.Session.get')
    def test_api_get_questions_200(self, mock_requests, mock_lambda_context, mock_parliament_questions_api_uri, mock_api_questions, sqs_client, create_sqs_queue, create_last_run_parameter):
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_api_questions)
        mock_response.json.return_value = mock_api_questions
        mock_response.status_code = 200

        event = {
            'startDate': '2024-01-01',
            'endDate': '2024-01-07'
        }
        context = mock_lambda_context        
        mock_requests.return_value = mock_response
        payload = lambda_handler(event, context)
        assert payload['statusCode'] == 200
        assert payload['body']['Count'] == mock_api_questions['totalResults']

        response = sqs_client.get_queue_attributes(QueueUrl=os.environ['QUESTION_QUEUE'], AttributeNames=['ApproximateNumberOfMessages'])
        assert int(response['Attributes']['ApproximateNumberOfMessages']) == mock_api_questions['totalResults']

    @patch('parliament_api_client.requests.Session.get')
    def test_api_get_questions_500(self, mock_requests, mock_lambda_context, mock_parliament_questions_api_uri, mock_api_questions, sqs_client, create_sqs_queue, create_last_run_parameter):
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_api_questions)
        mock_response.json.return_value = mock_api_questions
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('HTTP Error')
        mock_response.status_code = 500
        
        event = {
            'startDate': '2024-01-01',
            'endDate': '2024-01-07'
        }
        context = mock_lambda_context
        
        mock_requests.return_value = mock_response
        payload = lambda_handler(event, context)
        assert payload['statusCode'] == 500