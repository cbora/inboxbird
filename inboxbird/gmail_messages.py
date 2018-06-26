from __future__ import print_function

from flask import session, request, render_template, jsonify
from inboxbird import app
from flask_login import login_required

from utils import get_service, get_user_id
from apiclient import errors

from email.MIMEText import MIMEText
import base64

import gmail_labels


def create_message(sender, to, subject, message_text):
    """Create a message for an email.
    Args:
         sender: Email address of the sender.
         to: Email address of the receiver.
         subject: The subject of the email message.
         message_text: The text of the email message.
    Returns:
         An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def list_message_with_labels(label_ids):
    service = get_service()
    user_id = get_user_id()
    try:
        response = service.users().messages().list(userId=user_id,
                                                   labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId=user_id,
                                                           labelIds=label_ids,
                                                           pageToken=page_token).execute()
                messages.extend(response['messages'])
        return messages
    except errors.HttpError, error:
        print('An error occured: {}'.format(error))


@app.route('/list-msg-labels/<label>')
@login_required
def list_msg_labels(label):
    labels = [label]
    results = list_message_with_labels(labels)
    return jsonify(results)


def inboxbird_msg_read():
    label_id = get_label_id('InboxBird_READ')
    return {'removeLabelIds': [], 'addLabelIds': [label_id]}


def inboxbird_msg_unread():
    label_id = get_label_id('InboxBird_UNREAD')
    return {'removeLabelIds': [], 'addLabelIds': [label_id]}


def modify_labels_on_message(msg_id, msg_labels):
    service = get_service()
    user_id = get_user_id()
    try:
        message = service.users().messages().modify(userId=user_id,
                                                    id=msg_id,
                                                    body=msg_labels).execute()
        label_ids = message['labelIds']
        print('Message: {}  labels ids: {}'.format(msg_id, label_ids))
        return message
    except errors.HttpError, error:
        print('An error occured: {}'.format(error))


@app.route('/inboxbird-unread/<msg_id>')
@login_required
def make_inboxbird_unread(msg_id):
    label_obj = inboxbird_msg_unread()
    results = modify_labels_on_message(msg_id, label_obj)
    return jsonify(results)


@app.route('/inboxbird-read/<msg_id>')
@login_required
def make_inboxbird_read(msg_id):
    label_obj = inboxbird_msg_read()
    results = modify_labels_on_message(msg_id, label_obj)
    return jsonify(results)


def get_label_id(label_name):
    results = gmail_labels.list_labels()
    labels = results['labels']
    for l in labels:
        if l['name'] == label_name:
            return l['id']


@app.route('/label-id/<label_name>')
@login_required
def app_get_label_id(label_name):
    label_id = get_label_id(label_name)
    return jsonify(label_id)


def get_inbox_message(msg_id):
    service = get_service()
    user_id = get_user_id()
    try:
        message = service.users().messages().get(userId=user_id,
                                                 id=msg_id).execute()
        print('Message snippet: {}'.format(message['snippet']))
        return message
    except errors.HttpError, error:
        print('An error occured: {}'.format(error))
        return error


@app.route('/read-message/<msg_id>')
@login_required
def read_message(msg_id):
    message = get_inbox_message(msg_id)
    return jsonify(message)
