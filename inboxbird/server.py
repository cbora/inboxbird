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

from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')


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
