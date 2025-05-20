import os
import sys

sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))

class TestProcessQuestions:
    def test_process_questions(self, question_kb_id, question_kb_ds_id, question_crawler_name, process_questions_event, mock_lambda_context):
        os.environ["QUESTIONS_KB_ID"] = question_kb_id
        os.environ["QUESTIONS_KB_DS_ID"] = question_kb_ds_id
        os.environ["CRAWLER_NAME"] = question_crawler_name
        from functions.process_questions.app import lambda_handler

        event = process_questions_event

        response = lambda_handler(event, mock_lambda_context)

        assert response['statusCode'] == 200
