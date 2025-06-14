class MockFindSimilarQuestions:
   def __init__(self):
    self.mock_find_similar_questions = {
      "resource": "/api/similar-questions",
      "path": "/api/similar-questions",
      "httpMethod": "GET",
      "queryStringParameters": {
          "question": "What is being done about poor pupil behaviour"
      },
      "multiValueQueryStringParameters": {
          "question": [
              "What is being done about poor pupil behaviour"
          ]
      },
      "pathParameters": None,
      "stageVariables": None,
      "headers": {
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "Accept-Encoding": "gzip, deflate, sdch",
          "Accept-Language": "en-US,en;q=0.8",
          "Cache-Control": "max-age=0",
          "CloudFront-Forwarded-Proto": "https",
          "CloudFront-Is-Desktop-Viewer": "true",
          "CloudFront-Is-Mobile-Viewer": "false",
          "CloudFront-Is-SmartTV-Viewer": "false",
          "CloudFront-Is-Tablet-Viewer": "false",
          "CloudFront-Viewer-Country": "US",
          "Host": "1234567890.execute-api.{dns_suffix}",
          "Upgrade-Insecure-Requests": "1",
          "User-Agent": "Custom User Agent String",
          "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
          "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
          "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
          "X-Forwarded-Port": "443",
          "X-Forwarded-Proto": "https"
      },
      "requestContext": {
          "accountId": "123456789012",
          "resourceId": "123456",
          "stage": "prod",
          "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
          "identity": {
              "cognitoIdentityPoolId": None,
              "accountId": None,
              "cognitoIdentityId": None,
              "caller": None,
              "apiKey": None,
              "sourceIp": "127.0.0.1",
              "cognitoAuthenticationType": None,
              "cognitoAuthenticationProvider": None,
              "userArn": None,
              "userAgent": "Custom User Agent String",
              "user": None
          },
          "resourcePath": "/{proxy+}",
          "httpMethod": "POST",
          "apiId": "1234567890"
      }
    }