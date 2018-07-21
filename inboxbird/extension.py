from __future__ import print_function

from flask import session, request, render_template, jsonify, send_file
from inboxbird import app
from models import EmailOpen, User

import datetime as dt
from inboxbird import gmail_messages


UNREAD_LABEL_NAME = 'InboxBird_UNREAD'
READ_LABEL_NAME = 'InboxBird_READ'


@app.route('/get-tracker')
def get_tracker():
    """
       Get tracker link
         called by extension

    """
    print("\n\n\n New request.... ")
    if request.args.get('user', None) is None:
        return jsonify({'success': 'false'})
    user = User.objects(email=request.args.get('user', None)).first()
    imgHTML = ''
    email = None
    if user:
        email = EmailOpen()
        email.author = user
        email.sender_user_agent = str(request.user_agent)
        email.save()
        imgHTML = '{}track/open?id={}'.format(request.url_root, email.id)
    else:
        imgHTML = '{}tracking/open?id={}&u=?'.format(request.url_root, 'aaaa', request.args.get('user'))
    data = {}
    data['html'] = imgHTML
    data['tid'] = str(email.id)
    return jsonify(data)


@app.route('/tracking/open')
def tracking_open():
    """
          Email recipient calls this to get element

    """
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
    #filename = 'static/emailopened.gif'
    filename = 'static/testpic.png'
    return send_file(filename, mimetype='image/gif')


@app.route('/new-compose')
def new_compose():
    print("new compose window")
    return jsonify({'success': 'new compose true'})


@app.route('/on-send')
def on_send():
    """  
        On message send
           - Start tracking 
           - Label message as unread
           - Fill Subject 
           - Fill recipients
           - Get message blurb


    """
    msgid = request.args.get('msgid', None)
    itemid = request.args.get('tid', None)

    if not msgid and not itemid:
        return jsonify({'success': 'false'})

    email = EmailOpen.objects(id=itemid).first()
    if not email and not email.start_tracking:
        return jsonify({'error': 'email not found'})

    email.start_tracking = True
    email.msg_id = msgid
    email.system_sent_date = dt.datetime.now()
    email.save()

    session['email'] = email.author.email
    #label_id = gmail_messages.get_label_id(UNREAD_LABEL_NAME)

    #if not label_id:
    #    return jsonify({'error': 'label not found'})

    labels_unread = gmail_messages.inboxbird_msg_unread()

    # place label on message
    rsp = gmail_messages.modify_labels_on_message(msgid, labels_unread)

    msg = gmail_messages.get_message_metadata(msgid)

    email.subject = msg['Subject']
    email.recipient = msg['Recipient']
    email.snippet = msg['Snippet']
    email.gmail_internal_date = msg['InternalDate']
    email.thread_id = msg['ThreadID']
    email.save()

    return jsonify({'success': 'on send true'})


@app.route('/body-changed')
def body_changed():
    print("Body changed")
    return jsonify({'success': 'body changed true'})


@app.route('/token')
def get_token():
    return jsonify({'token': session.get('google_token')[0]})
