from flask import session
from flask_login import current_user

import httplib2
from googleapiclient.discovery import build
from oauth2client.client import AccessTokenCredentials
import google.oauth2.credentials
#from inboxbird.account3 import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_SCOPE
from models import User
import datetime as dt
from pprint import pprint


def get_service3():
    access_token = session.get('google_token')[0]
    user_agent = "my-user-agent"
    credentials = AccessTokenCredentials(access_token, user_agent)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('gmail', 'v1', http=http)
    return service


"""
def get_service2():
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
"""


def get_service(user_email=None):
    if user_email is None and current_user.is_authenticated:
        user_email = current_user.email
    elif user_email is None and session.get('email'):
        user_email = session.get('email')
    else:
        return None
    user = User.objects(email=user_email).first()    
    credentials = google.oauth2.credentials.Credentials(**user.gg_token)
    user.gg_token = credentials_to_dict(credentials)
    user.gg_token_last_updated = dt.datetime.now()
    user.save()
    service = build('gmail', 'v1', credentials=credentials)
    return service


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def get_user_id():
    user_id = 'me'
    return user_id
