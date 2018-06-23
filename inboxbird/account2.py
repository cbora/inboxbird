from inboxbird import app, login_manager
from flask import flash, url_for, current_app, render_template
from flask import request, Response, json, redirect, jsonify, send_file
from flask_login import login_required, current_user
from flask import session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, AnonymousUser, EmailOpen

from werkzeug.security import check_password_hash, generate_password_hash

login_manager.anonymous_user = AnonymousUser

import os
from flask_oauth import OAuth
from requests_oauthlib import OAuth2Session
from urllib2 import HTTPError

#from flask_oauthlib.client import OAuth2


#GOOGLE_CLIENT_ID = '376292480667-4j297tue1elkr2utp2h6c17j7i4q92im.apps.googleusercontent.com'
#GOOGLE_CLIENT_SECRET = 'aZGQo7laQVJyPjuHM1BCIXHE'

GOOGLE_CLIENT_ID = '376292480667-ctse957mbi2afhv61rjk63umki6hnesd.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'YyQ7QcF-pOyremLUD369a76A'

AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
REDIRECT_URI = 'http://localhost:5000/gg-oauth-authorized'
SCOPE = ['email', 'profile']



def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(GOOGLE_CLIENT_ID,
                             token=token)
    if state:
        return OAuth2Session(GOOGLE_CLIENT_ID,
                             state=state,
                             redirect_uri=REDIRECT_URI)
    oauth = OAuth2Session(GOOGLE_CLIENT_ID,
                          redirect_uri=REDIRECT_URI,
                          scope=SCOPE)
    return oauth


@app.route('/login')
def login():
    #if current_user.is_authenticated:
    #    return redirect(url_for('dashboard'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login3.html', auth_url=auth_url)


@app.route('/gg-oauth-authorized')
def callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has successfully authenticated our app.
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(TOKEN_URI,
                                       client_secret=GOOGLE_CLIENT_SECRET,
                                       authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(USER_INFO)
        print resp
        if resp.status_code == 200:
            me = resp.json()
            print me
            user = User.objects(gg_id=me['id']).first()
            if not user:
                user = User()
                user.gg_id = me['id']
                user.first_name = me['given_name']
                user.last_name = me['family_name']
                user.email = me['email']
                #user.gg_token = me['access_token']
                user.password = generate_password_hash(os.urandom(10), method='pbkdf2:sha256', salt_length=8)
                user.social_id = 1 # for google
                user.avatar = me['picture']
                user.locale = me['locale']
                #user.gender = me['gender']
                #user.save()

            login_user(user)
            return redirect(url_for('dashboard'))
        return 'Could not fetch your information.'


@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()
