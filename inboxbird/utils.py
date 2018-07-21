from flask import session

import httplib2
from googleapiclient.discovery import build
from oauth2client.client import AccessTokenCredentials
import google.oauth2.credentials
from inboxbird.account3 import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_SCOPE


def get_service3():
    access_token = session.get('google_token')[0]
    user_agent = "my-user-agent"
    credentials = AccessTokenCredentials(access_token, user_agent)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('gmail', 'v1', http=http)
    return service


def get_service():
    access_token = session.get('google_token')[0]
    refresh_token = session.get('google_token')[1]
    credentials = google.oauth2.credentials.Credentials(**{
        'token': access_token,
        'refresh_token': refresh_token,
        'token_uri': 'https://accounts.google.com/o/oauth2/token',
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'scopes': GOOGLE_SCOPE})
    # save credentials back to session in case they expired
    session['google_token'] = (credentials.token, credentials.refresh_token)
    service = build('gmail', 'v1', credentials=credentials)
    return service


def get_user_id():
    user_id = 'me'
    return user_id
