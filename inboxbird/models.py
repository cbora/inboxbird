from flask_mongoengine import MongoEngine
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import check_password_hash
import datetime as dt
from mongoengine.queryset import queryset_manager

from inboxbird import db

class User(UserMixin, db.Document):

    email = db.StringField(required=True, max_length=255)
    password = db.StringField(required=True, max_length=300)
    first_name = db.StringField(max_length=255)
    last_name = db.StringField(max_length=255)
    authenticated = True  # BooleanField(required=True, default=True)
    is_active = True  # BooleanField(required=True, default=True)
    role = db.StringField(default="User")
    is_admin = db.BooleanField(default=False)

    timezone = db.StringField()
    
    created_at = db.DateTimeField(default=dt.datetime.now)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_id(self):
        return str(self.id)

    def is_administrator(self):
        return self.is_admin

    def validate_login(self, input_password):
        return check_password_hash(self.password,input_password)


class AnonymousUser(AnonymousUserMixin):

    def __init__(self):
        self.email = None
        self.username = None

    def get_id(self):
        return None

    def is_anonymous(self):
        return True

    def is_administrator(self):
        return False


class EmailOpen(db.Document):
    sent_date = db.DateTimeField(default=dt.datetime.now)
    subject = db.StringField()
    recipient = db.StringField()
    message_blurb = db.StringField()
    gmail_msg_id = db.StringField()
    open_date = db.DateTimeField()    
    open_date_two = db.DateTimeField()
    tmp_id = db.StringField()
    number_opened = db.IntField(default=0)
    author = db.ReferenceField(User)
    sender_email = db.StringField()

    created_at = db.DateTimeField(default=dt.datetime.now)
