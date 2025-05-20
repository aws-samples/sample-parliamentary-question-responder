import requests
import json


class TestSuggestAnswer:
    def test_suggest_answer(
        self, site_cloudfront_url, get_id_token, populate_knowledge_base
    ):

        headers = {
            "Authorization": f"Bearer {get_id_token}",
            "Content-Type": "application/json",
        }

        body = {"prompt": "What is the government doing to improve education services?"}

        response = requests.post(
            f"{site_cloudfront_url}/api/suggest-answer",
            headers=headers,
            json=body,
            timeout=60,
        )
        assert response.status_code == 200
        assert len(response.text) > 0

    def test_suggest_answer_in_conversation(
        self, site_cloudfront_url, get_id_token, populate_knowledge_base
    ):

        headers = {
            "Authorization": f"Bearer {get_id_token}",
            "Content-Type": "application/json",
        }

        body = {
            "prompt": "What is the government doing to improve education services?"
        }

        response = requests.post(
            f"{site_cloudfront_url}/api/suggest-answer",
            headers=headers,
            json=body,
            timeout=60,
        )
        assert response.status_code == 200
        assert len(response.text) > 0

        params = {
            "session_id": response.json()["sessionId"]
        }

        body = {
            "prompt": "Can you make this just three points?",
        }

        response = requests.post(
            f"{site_cloudfront_url}/api/suggest-answer",
            headers=headers,
            params=params,
            json=body,
            timeout=60,
        )
        assert response.status_code == 200
        assert len(response.text) > 0
