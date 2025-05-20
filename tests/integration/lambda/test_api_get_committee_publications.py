import os

import sys

sys.path.append(".")
sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))

from tests.mock_data.mock_lambda_context import LambdaContext
from tests.environment.environment import stack_name


class TestAPIGetCommitteePublications:
    def test_api_get_committee_publications(self, publication_queue_name):
        event = {"committeeId": 203, "startDate": "2024-12-01", "endDate": "2024-12-31"}
        context = LambdaContext({})
        os.environ["PUBLICATION_QUEUE"] = publication_queue_name
        os.environ["COMMITTEE_API_BASE_URI"] = (
            "https://committees-api.parliament.uk/api/"
        )

        from functions.api_get_committee_publications.app import lambda_handler

        payload = lambda_handler(event, context)
        assert payload["statusCode"] == 200
