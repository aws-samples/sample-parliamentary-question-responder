import os
import json

import sys

sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))

from tests.mock_data.mock_lambda_context import LambdaContext

class TestFindSimilarQuestion:
    def test_find_similar_question(self, similar_questions_flow_alias_id, similar_questions_flow_id, mock_find_similar_questions, mock_lambda_context):
        
        os.environ["SIMILAR_QUESTIONS_FLOW_ALIAS_ID"] = similar_questions_flow_alias_id
        os.environ["SIMILAR_QUESTIONS_FLOW_ID"] = similar_questions_flow_id

        from functions.find_similar_questions.app import lambda_handler

        event = mock_find_similar_questions
        context = mock_lambda_context

        response = lambda_handler(event, context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body["questions"]) >= 1