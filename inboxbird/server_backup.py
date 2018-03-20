from mozcall import app, login_manager
from flask import flash, url_for, current_app, render_template, request, Response, json, redirect, jsonify
from flask_login import login_required, current_user
import datetime as dt
from models import User, AnonymousUser, EmailOpen
#from email_client import sendMeEmail

from forms import SignupForm, LoginForm
from forms import EmailTemplateForm, TextTemplateForm, EventForm

#from email.utils import parseaddr
import random

from flask import session

from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from flask_oauthlib.client import OAuth
from werkzeug.security import check_password_hash, generate_password_hash


# From Howididthis
# Change them maybe
GOOGLE_CLIENT_ID = '217837062348-omev9vu9rr3naaun4fmleqp0m0nr9spm.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '8_FuNyBHz_tXVY2Q0c6wafO-'

oauth = OAuth(app)

login_manager.anonymous_user = AnonymousUser

google = oauth.remote_app('google',
                          request_token_params={
                              'scope': 'email'
                          },
                          base_url='https://www.googleapis.com/oauth2/v1/',
                          request_token_url=None,
                          access_token_method='POST',
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == "GET":
        return render_template('signup.html', form=form, error=False)

    elif request.method == "POST":
        error, errors = form.validate()
        if form.validate_on_submit():
            user_obj = form.create_new_user()
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            return render_template('signup.html', form=form, error=True, errors=errors)


@app.route('/login')
def login():
    form = LoginForm()
    error = False

    if request.method == "GET":
        next_url = request.args.get('next_url', url_for('index'))
        return render_template('login.html', form=form)

    elif request.method == "POST":
        next_url = form.next_url
        user_obj = User.objects(email=form.username.data).first()
        if user_obj and user_obj.validate_login(form.password.data):
            login_user(user_obj)
            return redirect(next_url)
        else:
            error = True
            return render_template('login.html', form=form, error=error, errors=['Wrong username or password'])

@google.tokengetter
def get_google_token(token=None):
    return session.get('google_token')


@app.route('/gg-authorize')
def gg_login():
    return google.authorize(callback=url_for('.gg_oauth_authorized', _external=True))


@app.route('/gg-oauth-authorized')
@google.authorized_handler
def gg_oauth_authorized(resp):
    #resp = google.authorized_response()
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)

    session['google_token'] = (
        resp['access_token'],
        ''
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
        return redirect(url_for('edit_profile'))
    return redirect(next_url)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.objects(id=current_user.id).first()
    opens = EmailOpen.objects(author=user).all()
    return render_template('dashboard.html', opens=opens, author=user)


@app.route('/api/open')
def track_open():
    itemid = request.args.get('id', None)
    if itemid:
        opened = EmailOpen.objects(id=itemid).first()
        if opened:
            if opened.number_opened > 2:
                opened.number_opened += 1
                opened.save()
            elif opened.number_opened > 1:
                opened.open_date_two = dt.datetime.now()
                opened.number_opened += 1
                opened.save()
            elif opened.number_opened == 0:
                opened.open_date = dt.datetime.now()
                opened.number_opened += 1
                opened.save()
    return jsonify("{success: true}")


@app.route('/api/create-open', methods=['GET', 'POST'])
@login_required
def create_open():
    if request.method == 'POST':
        subject = request.form.get('sbj', None)
        sender_email = request.form.get('sdr-email', None)
        receiver = request.form.get('receiver', None)
        gmail_msg_id = request.form.get('gid', None)

        user = User.objects(id=current_user.id).first()
        opened = EmailOpen()
        opened.subject = subject
        opened.sent_date = dt.datetime.now()
        opened.receiver = receiver
        opened.gmail_msg_id = gmail_msg_id
        opened.author = user
        opened.sender_email = sender_email
        opened.save()
        return jsonify("{success: true}")

    return jsonify("{success: false}")
