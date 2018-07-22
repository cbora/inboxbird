from __future__ import print_function

import flask
from inboxbird import app, login_manager

from flask_login import login_user, logout_user, login_required, current_user

from models import User

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from werkzeug.security import check_password_hash, generate_password_hash

import os

import json

import datetime as dt
import requests

from pprint import pprint


GOOGLE_CLIENT_ID = '376292480667-4j297tue1elkr2utp2h6c17j7i4q92im.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'aZGQo7laQVJyPjuHM1BCIXHE'
GOOGLE_SCOPE = ['https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://mail.google.com/']

GOOGLE_CONFIG = {"web":{"client_id":"376292480667-4j297tue1elkr2utp2h6c17j7i4q92im.apps.googleusercontent.com","project_id":"inboxbird","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"aZGQo7laQVJyPjuHM1BCIXHE","redirect_uris":["http://localhost:5000/gg-oauth-authorized","http://inboxbird.com/gg-oauth-authorized"],"javascript_origins":["http://localhost:5000","http://inboxbird.com"]}}



@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.route('/login')
def login():
    if flask.request.method == 'GET':
        next_url = flask.request.args.get('next_url', flask.url_for('dashboard'))
        return flask.render_template('login2.html')


@app.route('/gg-authorize')
def gg_login():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(GOOGLE_CONFIG, GOOGLE_SCOPE)

    flow.redirect_uri = flask.url_for('gg_oauth_authorized', _external=True)


    authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/gg-oauth-authorized')
def gg_oauth_authorized():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(GOOGLE_CONFIG, GOOGLE_SCOPE)


    flow.redirect_uri = flask.url_for('gg_oauth_authorized', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)


    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    mycredentials = google.oauth2.credentials.Credentials(
        **credentials_to_dict(credentials))
    # Get User Profile Information
    profile = googleapiclient.discovery.build(
        'oauth2', 'v1', credentials=mycredentials)

    me = profile.userinfo().get().execute()

    user = User.objects(gg_id=me['id']).first()
    if not user:
        user = User()
        user.gg_id = me['id']
        user.first_name = me['given_name']
        user.last_name = me['family_name']
        user.email = me['email']
        user.avatar = me['picture']
        user.locale = me['locale']
        user.password = generate_password_hash(os.urandom(10), method='pbkdf2:sha256', salt_length=8)
        user.social_id = 1 # for google
        user.save()
    else:
        pass
    user.gg_token.update(credentials_to_dict(mycredentials))
    user.gg_token_last_updated = dt.datetime.now()
    user.last_login = dt.datetime.now()
    user.save()

    login_user(user)


    #files = drive.files().list().execute()
    #user_info = profile.
    flask.session['credentials'] = user.gg_token

    return flask.redirect(flask.url_for('dashboard'))


def credentials_to_dict(credentials):
    d = {'token': credentials.token,
         'token_uri': credentials.token_uri,
         'client_id': credentials.client_id,
         'client_secret': credentials.client_secret,
         'scopes': credentials.scopes}

    if credentials.refresh_token:
        d['refresh_token'] = credentials.refresh_token
    return d

@app.route('/logout')
@login_required
def logout():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    logout_user()
    return flask.redirect(flask.url_for('home'))


@app.route('/check')
def check():
    credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

    profile = googleapiclient.discovery.build(
        'oauth2', 'v1', credentials=credentials)

    userinfo = profile.userinfo().get().execute()

    print("user info: ", userinfo)
    print('session: ', flask.session['credentials'])
