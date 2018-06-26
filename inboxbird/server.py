from inboxbird import app, login_manager
from flask import flash, url_for, current_app, render_template
from flask import request, Response, json, redirect, jsonify, send_file
from flask_login import login_required, current_user
import datetime as dt
from models import User, AnonymousUser, EmailOpen

from forms import SignupForm, LoginForm, NewEmailForm
import random

from flask import session

from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from werkzeug.security import check_password_hash, generate_password_hash

login_manager.anonymous_user = AnonymousUser

import os




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = SignupForm()
    
    if request.method == "GET":
        return render_template('signup.html', form=form, error=False)

    elif request.method == "POST":
        error, errors = form.validate()
        if form.validate_on_submit():
            user_obj = form.create_new_user()
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', form=form, error=True, errors=errors)


def login2():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    error = False

    if request.method == "GET":
        next_url = request.args.get('next_url', url_for('index'))
        return render_template('login.html', form=form)

    elif request.method == "POST":
        user_obj = User.objects(email=form.username.data).first()
        if user_obj and user_obj.validate_login(form.password.data):
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            error = True
            return render_template('login.html', form=form, error=error, errors=['Wrong username or password'])



@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/settings')
@login_required
def settings():
    user = User.objects(id=current_user.id).first()
    return render_template('settings.html',
                           page_title='Settings',
                           user=user)


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.objects(id=current_user.id).first()
    opens = EmailOpen.objects(author=user).order_by('-sent_date').all()
    return render_template('dashboard.html',
                           emails=opens,
                           page_title='Dashboard',
                           user=user)

@app.route('/archive-email')
@login_required
def archive_email():
    return redirect(url_for('dashboard'))

@app.route('/track/open')
def track_open():
    itemid = request.args.get('id', None)
    if itemid:
        opened = EmailOpen.objects(id=itemid).first()
        if opened and opened.start_tracking:
            if opened.number_opened > 2:
                opened.number_opened += 1
                opened.save()
            elif opened.number_opened > 0:
                opened.open_date_two = dt.datetime.now()
                opened.number_opened += 1
                opened.save()
            elif opened.number_opened == 0:
                opened.open_date = dt.datetime.now()
                opened.number_opened += 1
                opened.save()
    filename = 'static/emailopened.gif'
    return send_file(filename, mimetype='image/gif')



@app.route('/start-tracking/<eid>')
@login_required
def start_tracking(eid):
    email = EmailOpen.objects(id=eid).first()
    email.start_tracking = True
    email.save()
    return redirect(url_for('dashboard'))


@app.route('/get')
def get_image():
    filename = 'static/emailopened.gif'
    return send_file(filename, mimetype='image/gif')



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


@app.route('/email-created/<email_id>')
@login_required
def email_success(email_id):

    
    text = '<img id="inboxbirdtracker" src="{}/track/open?id={}" width="1" height="1" border="0" style="position: absolute; left: 0; top: 0; width: 1px; height: 1px; opacity: 0.01;">'.format('http://www.inboxbird.com', str(email_id))

    user = User.objects(id=current_user.id).first()        
    return render_template('email-created.html',
                           email_id=email_id,
                           page_title='Email Created',
                           link=text)                           


@app.route('/new-email', methods=['GET', 'POST'])
@login_required
def new_email_form():
    form = NewEmailForm()

    user = User.objects(id=current_user.id).first()    

    if request.method == 'GET':
        form.refresh_from(current_user)
        return render_template('email-form.html',
                               page_title="New Email",
                               form=form,
                               error=False, errors=[],
                               user=user)

    elif request.method == 'POST':
        error, errors = form.validate()

        if not error:
            email = form.push_to_mongo(current_user)
            return redirect(url_for('email_success', email_id=email.id))
        else:
            return render_template('email-form.html',
                                   page_title="New Email",
                                   form=form,
                                   error=error, errors=errors,
                                   user=user)


@app.route('/edit-email', methods=['GET', 'POST'])
@login_required
def edit_email_form():
    form = NewEmailForm()

    user = User.objects(id=current_user.id).first()    

    if request.method == 'GET':
        email = EmailOpen()
        form.refresh_from(current_user)
        form.refresh_values(email)
        return render_template('email-form.html',
                               page_title="Edit Email",
                               form=form,
                               error=False, errors=[],
                               user=user)

    elif request.method == 'POST':
        error, errors = form.validate()

        if not error:
            email = EmailOpen()
            new_email = form.update_values(email)
            return redirect(url_for('email_success', email_id=new_email.id))
        else:
            return render_template('email-form.html',
                                   page_title="Edit Email",
                                   form=form,
                                   error=error, errors=errors,
                                   user=user)
