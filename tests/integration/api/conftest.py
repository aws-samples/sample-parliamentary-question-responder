import pytest
import boto3
import secrets

from pycognito.aws_srp import AWSSRP

COGNITO_USER_NAME = 'dummy@test.com'
@pytest.fixture(scope='module')
def username():
  return COGNITO_USER_NAME

@pytest.fixture(scope='module')
def password():
  password_length = 20
  return secrets.token_urlsafe(password_length) + '!'

@pytest.fixture(scope='module')
def create_test_user(aws_region, user_pool_id, user_pool_client_id, username, password):
  cognito_client = boto3.client('cognito-idp', region_name=aws_region)

  try:
      cognito_client.admin_get_user(
        UserPoolId=user_pool_id,
        Username=username
      )
  except cognito_client.exceptions.UserNotFoundException:
      cognito_client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        MessageAction='SUPPRESS',
        TemporaryPassword=password,
        UserAttributes=[
          {
            'Name': 'email',
            'Value': username
          },
          {
            'Name': 'email_verified',
            'Value': 'true'
          }
        ],
      )

  cognito_client.admin_set_user_password(
    UserPoolId=user_pool_id,
    Username=username,
    Password=password,
    Permanent=True
  )

  yield

  cognito_client.admin_delete_user(
    UserPoolId=user_pool_id,
    Username=username
  )

@pytest.fixture(scope='module')
def get_cognito_auth(create_test_user, aws_region, user_pool_id, user_pool_client_id, username, password):
    cognito_client = boto3.client('cognito-idp', region_name=aws_region)
    aws_srp = AWSSRP(
       username=username,
       password=password,
       pool_id=user_pool_id,
       client_id=user_pool_client_id,
       client=cognito_client
    )

    try:       
      tokens = aws_srp.authenticate_user()
      if 'AuthenticationResult' in tokens:
        return {
           'id_token': tokens['AuthenticationResult']['IdToken'],
           'refresh_token': tokens['AuthenticationResult']['RefreshToken'],
           'access_token': tokens['AuthenticationResult']['AccessToken']
        }
      else:
         raise RuntimeError("Authentication failed")
    except Exception as e:
        raise RuntimeError(f"Authentication error: {str(e)}") from e

@pytest.fixture(scope='module')
def get_id_token(get_cognito_auth):
    return get_cognito_auth['id_token']

@pytest.fixture(scope='module')
def get_access_token(get_cognito_auth):
    return get_cognito_auth['access_token']