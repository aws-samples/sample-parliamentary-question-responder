import requests
import json

class TestFindSimilarQuestions:
    def test_find_similar_questions(self, site_cloudfront_url, get_id_token, populate_knowledge_base):

        params = {'question': 'What is being done about poor pupil behaviour'}
        headers = {
            'Authorization': f'Bearer {get_id_token}',
            'Content-Type': 'application/json'
            }

        response = requests.get(
            f'{site_cloudfront_url}/api/similar-questions',
            params=params,
            headers=headers,
            timeout=30)
        assert response.status_code == 200

        questions = json.loads(response.text)['questions']

        assert len(questions) > 0