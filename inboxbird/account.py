from inboxbird import app, login_manager
from flask import flash, url_for, current_app, render_template
from flask import request, Response, json, redirect, jsonify, send_file
from flask_login import login_required, current_user
from flask import session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, AnonymousUser, EmailOpen

from werkzeug.security import check_password_hash, generate_password_hash

login_manager.anonymous_user = AnonymousUser

from flask_oauthlib.client import OAuth
import os


GOOGLE_CLIENT_ID = '376292480667-4j297tue1elkr2utp2h6c17j7i4q92im.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'aZGQo7laQVJyPjuHM1BCIXHE'
GOOGLE_SCOPE = ['email',
                'profile',
                'https://mail.google.com/',
                'https://www.googleapis.com/auth/userinfo.email']

oauth = OAuth()


google = oauth.remote_app('google',
                          request_token_params={
                              'scope': GOOGLE_SCOPE,
                              'access_type': 'offline'
                          },
                          base_url='https://www.googleapis.com/oauth2/v1/',
                          request_token_url=None,
                          access_token_method='POST',
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET
                          )



@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.route('/login')
def login():
    if request.method == 'GET':
        next_url = request.args.get('next_url', url_for('dashboard'))
        return render_template('login2.html')


@google.tokengetter
def get_google_token(token=None):
    return session.get('google_token')


@app.route('/gg-authorize')
def gg_login():
    return google.authorize(callback=url_for('gg_oauth_authorized', _external=True))


@app.route('/gg-oauth-authorized')
@google.authorized_handler
def gg_oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('dashboard')
    if resp is None:
        return redirect(next_url)

    print("response")
    print(resp.keys())

    print('\n\n\n')
    print(resp)
    #print(resp['t'])    
    session['google_token'] = (
        resp['access_token'],
        resp['refresh_token']
        )
    me = google.get('userinfo')
    user = User.objects(gg_id=me.data['id']).first()
    print me.data
    if not user:
        user = User()
        user.gg_id = me.data['id']
        user.first_name = me.data['given_name']
        user.last_name = me.data['family_name']
        user.email = me.data['email']
        user.gg_token = resp['access_token']
        user.password = generate_password_hash(os.urandom(10), method='pbkdf2:sha256', salt_length=8)
        user.social_id = 1 # for google
        user.save()

    login_user(user)
    if not user.first_name or not user.last_name:
        #return redirect(url_for('edit_profile'))
        pass
    return redirect(next_url)


@app.route('/logout')
@login_required
def logout():
    session.pop('google_token')
    logout_user()
    return redirect(url_for('home'))
