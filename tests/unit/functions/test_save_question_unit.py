import pytest
import json
import os
import sys
sys.path.append('.')
sys.path.append(os.path.join(os.getcwd(), 'layers', 'pq-responder'))
import boto3

from dateutil import parser

from unittest.mock import patch, MagicMock
from moto import mock_aws

from models import Question, House

@mock_aws
class TestSaveQuestion():

    @pytest.fixture()
    def mock_sqs_complete_question(self):
        from tests.mock_data.mock_sqs_question import MockSQSQuestion
        yield MockSQSQuestion().mock_sqs_complete_question
    
    @pytest.fixture()
    def mock_sqs_incomplete_question(self):
        from tests.mock_data.mock_sqs_question import MockSQSQuestion
        yield MockSQSQuestion().mock_sqs_incomplete_question

    def test_save_complete_question_200(self, mock_sqs_complete_question, mock_lambda_context, s3_client, create_question_s3_bucket, mock_parliament_questions_api_uri):
        from functions.save_question.app import lambda_handler

        event = mock_sqs_complete_question
        context = mock_lambda_context
        
        payload = lambda_handler(event, context)
        assert payload['statusCode'] == 200

        json_question = json.loads(event['Records'][0]['body'])
        question = Question(
            id=json_question['id'],
            house=House(json_question['house'].lower()),
            date_tabled=parser.parse(json_question['date_tabled']),
            question=json_question['question'],
            answer=json_question['answer']
        )
        key=f'question_type=written/year={question.date_tabled.year:04d}/month={question.date_tabled.month:02d}/day={question.date_tabled.day:02d}/{question.id}.json'
        s3_object = s3_client.get_object(
            Bucket=os.environ['QUESTIONS_BUCKET'], 
            Key=key
        )
        if s3_object.get('ResponseMetadata'):
            assert s3_object['ResponseMetadata']['HTTPStatusCode'] == 200
        else:
            raise AssertionError('Error getting object from S3')
        
        assert s3_object['Body'].read().decode('utf-8') == question.model_dump_json()

    @patch('parliament_api_client.requests.Session.get')
    def test_save_incomplete_question_200(self, mock_requests, mock_api_question, mock_sqs_incomplete_question, mock_lambda_context, mock_parliament_questions_api_uri, s3_client, create_question_s3_bucket):
        from functions.save_question.app import lambda_handler

        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_api_question)
        mock_response.json.return_value = mock_api_question
        mock_response.status_code = 200

        event = mock_sqs_incomplete_question
        context = mock_lambda_context
        
        mock_requests.return_value = mock_response
        payload = lambda_handler(event, context)
        assert payload['statusCode'] == 200

        json_question = json.loads(event['Records'][0]['body'])
        question = Question(
            id=json_question['id'],
            house=House(json_question['house'].lower()),
            date_tabled=parser.parse(json_question['date_tabled']),
            question=json_question['question'],
            answer=json_question['answer']
        )
        key=f'question_type=written/year={question.date_tabled.year:04d}/month={question.date_tabled.month:02d}/day={question.date_tabled.day:02d}/{question.id}.json'
        s3_object = s3_client.get_object(
            Bucket=os.environ['QUESTIONS_BUCKET'], 
            Key=key
        )
        if s3_object.get('ResponseMetadata'):
            assert s3_object['ResponseMetadata']['HTTPStatusCode'] == 200
        else:
            assert s3_object['Body'].read().decode('utf-8') == json.dumps(question.to_dict())
