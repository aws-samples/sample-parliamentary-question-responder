import os

import sys
sys.path.append(".")
sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))

class TestBuildContentKBResponse:
  def test_content_kb_response(self, content_kb_id, mock_flow_build_content_kb_response, mock_lambda_context):

    os.environ["CONTENT_KB_ID"] = content_kb_id
    from functions.build_content_kb_response.app import lambda_handler

    event = mock_flow_build_content_kb_response

    response = lambda_handler(event, mock_lambda_context)
    assert len(response) > 0 