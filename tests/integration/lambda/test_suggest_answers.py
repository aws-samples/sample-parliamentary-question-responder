import os
import json

import sys

sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))


class TestSuggestAnswers:

    def test_suggest_answers(
        self,
        suggest_answer_agent_alias_id,
        suggest_answer_agent_id,
        mock_suggest_answer,
        mock_lambda_context,
    ):

        os.environ["SUGGEST_ANSWER_AGENT_ALIAS_ID"] = suggest_answer_agent_alias_id
        os.environ["SUGGEST_ANSWER_AGENT_ID"] = suggest_answer_agent_id

        from functions.suggest_answer.app import lambda_handler

        event = mock_suggest_answer
        context = mock_lambda_context

        response = lambda_handler(event, context)

        assert response["statusCode"] == 200
        response_json = json.loads(response["body"])
        assert len(response_json["completion"]) >= 1

        session_id = response_json["sessionId"]

        event["queryStringParameters"] = {
            "session_id": session_id,
        }
        event["multiValueQueryStringParameters"] = {
            "session_id": [session_id],
        }
        event["body"] = json.dumps(
            {
                "prompt": "Can you reduce this to 3 points"
            }
        )

        response = lambda_handler(event, context)

        assert response["statusCode"] == 200
        response_json = json.loads(response["body"])
        assert len(response_json["completion"]) >= 1
