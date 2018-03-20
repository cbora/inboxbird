from flask_wtf import Form as FlaskForm
from wtforms.validators import DataRequired
from wtforms import (BooleanField, FieldList, RadioField, TextField, TextAreaField,
                    SubmitField, ValidationError, PasswordField, StringField, SelectField,
                     validators, SelectMultipleField, widgets, HiddenField, FileField)

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import datetime as dt


from models import User, EmailOpen

class LoginForm(FlaskForm):
    username = StringField(id='email', validators=[DataRequired()])
    password = PasswordField(id='pwd', validators=[DataRequired()])
    next_url = TextField(id='next_url')


class SignupForm(FlaskForm):
    name = TextField(id='name')
    password = PasswordField(id='password')
    email = TextField(id="email")

    def validate(self):
        user = User.objects(email=self.email.data).first()
        if user is None:
            return (False, [])
        else:
            return(True, ['Email is already taken'])


    def create_new_user(self):
        user = User()
        if len(self.name.data) > 1:
            user.first_name = self.name.data.split(' ')[0]
            user.last_name = self.name.data.split(' ')[1]
        else:
            user.first_name = self.name.data

        user.email = self.email.data
        user.password = generate_password_hash(self.password.data, method='pbkdf2:sha256', salt_length=8)
        user.save()

        return user


class NewEmailForm(FlaskForm):
    subject = TextField(id='subject')
    recipient = TextField(id='recipient')
    notes = TextAreaField(id='notes')
    sent_from = TextField(id='sent_from')

    def refresh_from(self, current_user):
        user = User.objects(id=current_user.id).first()
        self.sent_from.data = user.email

    def validate(self):
        return (False, [])

    def refresh_values(self, email):
        self.subject.data = email.subject
        self.recipient.data = email.recipient
        self.notes.data = email.notes
        self.sent_from.data = email.sender_email

    def update_values(self, email):
        email.subject = self.subject.data
        email.recipient = self.recipient.data
        email.notes = self.notes.data
        email.sender_email = self.sent_from.data
        email.sent_date = dt.datetime.now()
        email.save()

        return email

    def push_to_mongo(self, current_user):
        email = EmailOpen()

        email.subject = self.subject.data
        email.recipient = self.recipient.data
        email.notes = self.notes.data
        email.sender_email = self.sent_from.data
        user = User.objects(id=current_user.id).first()
        email.author = user
        email.save()

        return email
