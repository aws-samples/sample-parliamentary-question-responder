class MockFlowBuildContentKBResponse:
   def __init__(self):
    self.mock_flow_build_content_kb_response = {
        "messageVersion": "1.0",
        "function": "BuildContentKBResponse",
        "parameters": [
            {
                "name": "Question",
                "type": "string",
                "value": "What is the government doing to improve education services?"
            }
        ],
        "sessionId": "d4df2ac2-8a56-40c4-8481-f61431eb7e88",
        "agent": {
            "name": "pq-responder-1-SuggestAnswerAgent",
            "version": "1",
            "id": "K1AUX9UYI0",
            "alias": "SZDT6VSDB4"
        },
        "actionGroup": "GetOfficialContent",
        "sessionAttributes": {},
        "promptSessionAttributes": {},
        "inputText": "What is the government doing to improve education services?"
    }
