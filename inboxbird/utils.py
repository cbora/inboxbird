from flask import session

import httplib2
from googleapiclient.discovery import build
from oauth2client.client import AccessTokenCredentials


def get_service():
    access_token = session.get('google_token')[0]
    user_agent = "my-user-agent"
    credentials = AccessTokenCredentials(access_token, user_agent)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('gmail', 'v1', http=http)
    return service


def get_user_id():
    user_id = 'me'
    return user_id
