from __future__ import print_function

from flask import session, request, render_template, jsonify
from inboxbird import app
from flask_login import login_required

from utils import get_service, get_user_id
from apiclient import errors

from email.MIMEText import MIMEText
import base64
import dateutil.parser as parser
from bs4 import BeautifulSoup

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
    return None


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


@app.route('/frm-msg/<msg_id>')
@login_required
def get_msg_mtd(msg_id):
    msg = get_message_metadata(msg_id)
    return jsonify(msg)


def get_message_metadata(msg_id):
    """
         # Get Formatted Messages
    """
    temp_dict = {}
    message = get_inbox_message(msg_id)
    payld = message['payload']  # get payload of the message
    headr = payld['headers']  # get header of the payload

    for one in headr:  # getting the Subject
        if one['name'] == 'Subject':
            msg_subject = one['value']
            temp_dict['Subject'] = msg_subject
        else:
            pass

    for two in headr:  # getting the date
        if two['name'] == 'Date':
            msg_date = two['value']
            date_parse = (parser.parse(msg_date))
            m_date = (date_parse)
            temp_dict['Date'] = str(m_date)
        else:
            pass

    for three in headr:  # getting the Sender
        if three['name'] == 'From':
            msg_from = three['value']
            temp_dict['Sender'] = msg_from
        else:
            pass

    for four in headr:
        if four['name'] == 'To':
            msg_to = four['value']
            temp_dict['Recipient'] = msg_to

    #fetching message message thread
    temp_dict['ThreadID'] = message['threadId']
    # fetching message snippet
    temp_dict['Snippet'] = message['snippet']
    temp_dict['InternalDate'] = message['internalDate']

    try:
        # Fetching message body
        mssg_parts = payld['parts']  # fetching the message parts
        part_one = mssg_parts[0]  # fetching first element of the part 
        part_body = part_one['body']  # fetching body of the message
        part_data = part_body['data']  # fetching data from the body
        clean_one = part_data.replace("-", "+")  # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_", "/")  # decoding from Base64 to UTF-8
        clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))  # decoding from Base64 to UTF-8
        soup = BeautifulSoup(clean_two, "lxml")
        mssg_body = soup.body()
        # mssg_body is a readible form of message body
        # depending on the end user's requirements,
        # it can be further cleaned
        # using regex, beautiful soup, or any other method
        temp_dict['Message_body'] = mssg_body
    except:
        print("failed to parse")

    print (temp_dict)
    return temp_dict
