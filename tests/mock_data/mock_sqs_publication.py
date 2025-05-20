class MockSQSPublication():
  def __init__(self):
    self.mock_sqs_complete_publication = {
      "Records": [
        {
          "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
          "receiptHandle": "MessageReceiptHandle",
          # "body": "{\"committee_id\":203,\"id\":46016,\"description\":\"Letter from DCMS Secretary of State on National Youth Strategy dated 06.12.24\",\"documents\":[{\"id\":229090,\"publication_id\":46016, \"files\":[{\"filename\":\"Letter from Secretary of State for Culture, Media and Sport to Chair (National Youth Strategy) 06.12.24.pdf\"}]}]}",
          "body": "{\"committee_id\":203,\"id\":41590,\"description\":\"Seventh Report - Persistent absence and support for disadvantaged pupils\",\"documents\":[{\"id\":205047,\"publication_id\":41590,\"files\":[{\"filename\":\"HC 970 - Persistent absence - v3-Online.pdf\"}],\"uri_path\":\"Publications/41590/Document/205047/OriginalFormat\"}]}",
          "attributes": {
            "ApproximateReceiveCount": "1",
            "SentTimestamp": "1523232000000",
            "SenderId": "123456789012",
            "ApproximateFirstReceiveTimestamp": "1523232000001"
          },
          "messageAttributes": {},
          "md5OfBody": "{{{md5_of_body}}}",
          "eventSource": "aws:sqs",
          "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
          "awsRegion": "us-east-1"
        }
      ]
    }

    self.mock_sqs_incomplete_question = {
      "Records": [
        {
          "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
          "receiptHandle": "MessageReceiptHandle",
          "body": "{\"committee_id\":203,\"id\": 1679416, \"house\": \"commons\", \"date_tabled\": \"2024-01-05T00:00:00\", \"question\": \"To ask the Secretary of State for Education, how many (a) starts and (b) completions of flexi-job apprenticeships there have been through the flexi-job apprenticeship agencies register since February 2022.\", \"answer\": \"The department is supporting sectors with short-term project-based work through flexi-Job apprenticeship agencies (FJAAs), which allow apprentices to work with different host employers, and on a range of projects, to gain the skills and knowledge needed t...\"}",
          "attributes": {
            "ApproximateReceiveCount": "1",
            "SentTimestamp": "1523232000000",
            "SenderId": "123456789012",
            "ApproximateFirstReceiveTimestamp": "1523232000001"
          },
          "messageAttributes": {},
          "md5OfBody": "{{{md5_of_body}}}",
          "eventSource": "aws:sqs",
          "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
          "awsRegion": "us-east-1"
        }
      ]
    }