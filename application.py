from flask import Flask
import os

application = Flask(__name__, static_folder='./inboxbird/static', template_folder='./inboxbird/templates')

from inboxbird import *
