import os

import sys

sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))

from tests.mock_data.mock_lambda_context import LambdaContext
from tests.mock_data.mock_sqs_publication import MockSQSPublication


class TestApiGetPublication:
    def test_get_publication(self, content_bucket_name):
        os.environ["CONTENT_BUCKET"] = content_bucket_name
        os.environ["COMMITTEE_API_BASE_URI"] = (
            "https://committees-api.parliament.uk/api/"
        )
        os.environ["COMMITTEE_BASE_URI"] = "https://committees.parliament.uk/"
        from functions.save_publication.app import lambda_handler

        event = MockSQSPublication().mock_sqs_complete_publication
        context = LambdaContext({})
        response = lambda_handler(event, context)
