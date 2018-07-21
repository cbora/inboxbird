from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
import os


app = Flask(__name__)
on_heroku = os.environ.get("ON_HEROKU", False)

if on_heroku:
    app.config['MONGODB_SETTINGS'] = {
        'host': 'mongodb://inboxbird:wallstreet12@ds119489.mlab.com:19489/inboxbird'
    }
else:
    app.config['MONGODB_SETTINGS'] = {
        'host': 'mongodb://inboxbird:wallstreet12@ds119489.mlab.com:19489/inboxbird'    
    }


login_manager = LoginManager()
login_manager.init_app(app)


app.secret_key = "asdhesakljklfasagwh39thgawdadsdadas4"
db = MongoEngine(app)

import inboxbird.models
import inboxbird.account3
import inboxbird.server
import inboxbird.gmail_drafts
import inboxbird.gmail_labels
import inboxbird.gmail_messages
import inboxbird.extension
if not on_heroku:
    from inboxbird.admin import admin_app
