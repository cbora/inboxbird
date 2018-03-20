from inboxbird import app

from models import User, EmailOpen
from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_admin.contrib.mongoengine import ModelView

from flask_admin.contrib.mongoengine import ModelView
from flask import render_template
from flask_admin.form import rules
from werkzeug.security import generate_password_hash
from wtforms import TextField, SelectField
from flask.ext import login
from flask_admin import BaseView, expose, AdminIndexView, Admin


class AdminModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        return render_template('unauthorized.html')


class QuickView(AdminModelView):
    page_size = 50


class AnalyticsView(AdminIndexView):
    @expose('/')
    def admin_index(self):
        if login.current_user.is_administrator():
            analytics = 1
            return self.render('admin/analytics.html', analytics=analytics)
        else:
            return self.render('unauthorized.html')


admin_app = Admin(app, index_view=AnalyticsView())
admin_app.add_view(QuickView(User))
admin_app.add_view(QuickView(EmailOpen))
