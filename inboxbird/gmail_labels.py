from __future__ import print_function

from flask import session, request, render_template, jsonify
from inboxbird import app
from flask_login import login_required

from utils import get_service, get_user_id
from apiclient import errors



def list_labels():
    service = get_service()
    user_id = get_user_id()
    results = service.users().labels().list(userId=user_id).execute()
    return results


@app.route('/labels')
@login_required
def get_labels():
    labels = list_labels()
    return jsonify(labels)


def make_label(label_name, mlv='show', llv='labelShow'):
    """Create Label object.

    Args:
        label_name: The name of the Label.
        mlv: Message list visibility, show/hide.
        llv: Label list visibility, labelShow/labelHide.

    Returns:
         Created Label.
    """
    label = {'messageListVisibility': mlv,
             'name': label_name,
             'labelListVisibility': llv}
    return label


def create_label(label_object):
    service = get_service()
    user_id = get_user_id()
    try:
        label = service.users().labels().create(userId=user_id, body=label_object).execute()
        label
    except errors.HttpError, error:
        print('An error occured: {}'.format(error))
        return jsonify(error)


@app.route('/new-label/<label_name>')
@login_required
def new_label(label_name):
    label_obj = make_label(label_name)
    label = create_label(label_obj)
    return jsonify(label)


def send_message(sender, to, subject, msg_txt):
    message_body = create_message(sender, to, subject, msg_txt)
    service = get_service()
    user_id = get_user_id()
    try:
        message =(service.users().messages().send(userId=user_id, body=message_body).execute())
        print('Message id: {}'.format(message['id']))
        return jsonify(message)
    except errors.HttError, error:
        print('An error occured: {}'.format(error))
        return jsonify(error)


def delete_label(label_id):
    service = get_service()
    label_id = ''
    user_id = get_user_id()
    try:
        service.users().labels().delete(userId=user_id, id=label_id).execute()
    except errors.HttpError, error:
        print('An error occured: {}'.format(error))
        return jsonify(error)
