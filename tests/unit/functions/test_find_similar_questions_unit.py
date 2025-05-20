import botocore.client
import pytest
import os
import json
import botocore

import sys
sys.path.append(".")
sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))

from unittest.mock import patch
from moto import mock_aws

orig = botocore.client.BaseClient._make_api_call


def mock_make_api_call(self, operation_name, kwarg):
    if operation_name == "InvokeFlow":
        return {
            "responseStream": [
                {
                    "flowOutputEvent": {
                        "content": {
                            "document": [
                                {
                                    "score": 0.51977736,
                                    "location": {
                                        "sharePointLocation": None,
                                        "salesforceLocation": None,
                                        "sqlLocation": None,
                                        "kendraDocumentLocation": None,
                                        "confluenceLocation": None,
                                        "customDocumentLocation": None,
                                        "s3Location": {
                                            "uri": "s3://questions_bucket/2024/01/08/1680580.json"
                                        },
                                        "type": "S3",
                                        "webLocation": None,
                                    },
                                    "metadata": {
                                        "x-amz-bedrock-kb-source-uri": {...},
                                        "x-amz-bedrock-kb-chunk-id": {...},
                                        "x-amz-bedrock-kb-data-source-id": {...},
                                    },
                                    "content": {
                                        "byteContent": None,
                                        "row": None,
                                        "text": '{"id": 1680580, "house": "commons", "date_tabled": "2024-01-08T00:00:00", "question": "To ask the Secretary of State for Education, if she will review the discipline guidance for schools to include the creation of more therapeutic educational environments.", "answer": "<p>In July 2022, the Department for Education published the updated \\u2018Behaviour in Schools\\u2019 guidance, which is the primary source of help and support for schools on developing and implementing a behaviour policy that can create a school culture with high expectations of behaviour.</p><p>Any school behaviour policy must be lawful, proportionate and reasonable and comply with the school\\u2019s duties under the Equality Act 2010 and the Education and Inspections Act 2006. Account must be taken of a pupil\\u2019s age, any Special Educational Needs or Disability they may have, and any religious requirements affecting them. Within these legal parameters, it is then for individual schools to develop their own policies.</p>"}',
                                        "type": "TEXT",
                                    },
                                }
                            ]
                        }
                    }
                },
                {"flowCompletionEvent": {"completionReason": "SUCCESS"}},
            ]
        }

    return orig(self, operation_name, kwarg)


@mock_aws
class TestFindSimilarQuestions:

    @pytest.fixture
    def mock_s3_question(self, s3_client, create_question_s3_bucket):
        s3_client.put_object(
            Bucket=os.environ["QUESTIONS_BUCKET"],
            Key="2024/01/08/1680580.json",
            Body=json.dumps({"id": 1680580, "house": "commons", "date_tabled": "2024-01-08T00:00:00", "question": "To ask the Secretary of State for Education, if she will review the discipline guidance for schools to include the creation of more therapeutic educational environments.", "answer": "<p>In July 2022, the Department for Education published the updated \u2018Behaviour in Schools\u2019 guidance, which is the primary source of help and support for schools on developing and implementing a behaviour policy that can create a school culture with high expectations of behaviour.</p><p>Any school behaviour policy must be lawful, proportionate and reasonable and comply with the school\u2019s duties under the Equality Act 2010 and the Education and Inspections Act 2006. Account must be taken of a pupil\u2019s age, any Special Educational Needs or Disability they may have, and any religious requirements affecting them. Within these legal parameters, it is then for individual schools to develop their own policies.</p>"}),
        )

    def test_find_similar_questions(
        self,
        mock_find_similar_questions,
        mock_lambda_context,
        mock_s3_question
    ):
        os.environ["SIMILAR_QUESTIONS_FLOW_ALIAS_ID"] = ""
        os.environ["SIMILAR_QUESTIONS_FLOW_ID"] = ""

        from functions.find_similar_questions.app import lambda_handler

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):
            payload = lambda_handler(mock_find_similar_questions, mock_lambda_context)

        assert payload["statusCode"] == 200
        body = json.loads(payload["body"])
        assert len(body["questions"]) == 1

    def test_find_similar_questions_question_too_short(
        self, mock_find_similar_questions, mock_lambda_context
    ):
        os.environ["SIMILAR_QUESTIONS_FLOW_ALIAS_ID"] = ""
        os.environ["SIMILAR_QUESTIONS_FLOW_ID"] = ""

        from functions.find_similar_questions.app import lambda_handler

        find_similar_questions_event = mock_find_similar_questions
        find_similar_questions_event["queryStringParameters"] = {"question": "Shrt"}
        find_similar_questions_event["multiValueQueryStringParameters"]["question"][
            0
        ] = "Shrt"
        payload = lambda_handler(find_similar_questions_event, mock_lambda_context)

        assert payload["statusCode"] == 422
        body = json.loads(payload["body"])
        assert body["detail"][0]["type"] == "string_too_short"

    def test_find_similar_questions_incorrect_query_string(
        self, mock_find_similar_questions, mock_lambda_context
    ):
        os.environ["SIMILAR_QUESTIONS_FLOW_ALIAS_ID"] = ""
        os.environ["SIMILAR_QUESTIONS_FLOW_ID"] = ""

        from functions.find_similar_questions.app import lambda_handler

        find_similar_questions_event = mock_find_similar_questions
        find_similar_questions_event["queryStringParameters"] = {"wrong": "wrong"}
        find_similar_questions_event["multiValueQueryStringParameters"]["wrong"] = [
            "wrong"
        ]
        find_similar_questions_event["multiValueQueryStringParameters"].pop("question")
        payload = lambda_handler(find_similar_questions_event, mock_lambda_context)

        body = json.loads(payload["body"])
        assert payload["statusCode"] == 422
        assert body["detail"][0]["type"] == "missing"
