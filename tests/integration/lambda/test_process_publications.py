import os
import sys

sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))

class TestProcessQuestions:
    def test_process_questions(self, content_kb_id, content_kb_publication_ds_id, process_publications_event, mock_lambda_context):
        os.environ["CONTENT_KB_ID"] = content_kb_id
        os.environ["CONTENT_KB_PUBLICATION_DS_ID"] = content_kb_publication_ds_id

        from functions.process_publications.app import lambda_handler

        event = process_publications_event

        response = lambda_handler(event, mock_lambda_context)

        assert response['statusCode'] == 200
