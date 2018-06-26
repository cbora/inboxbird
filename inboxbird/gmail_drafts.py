from __future__ import print_function

from flask import session, request, render_template, jsonify
from inboxbird import app
from flask_login import login_required

from utils import get_service, get_user_id
from apiclient import errors


def list_drafts():
    service = get_service()
    user_id = get_user_id()
    results = service.users().drafts().list(userId=user_id).execute()
    drafts = results['drafts']
    return drafts


@app.route('/drafts')
@login_required
def get_drafts():
    drafts = list_drafts()
    return jsonify(drafts)


def get_draft(draftid):
    service = get_service()
    user_id = get_user_id()
    results = service.users().drafts().get(userId=user_id, id=draftid).execute()
    return results


@app.route('/read-draft/<draftid>')
@login_required
def read_draft(draftid):
    draft = get_draft(draftid)
    return jsonify(draft)


def create_draft(message_body):
    service = get_service()
    user_id = get_user_id()
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()
        print('Draft id: {} \n message: {}'.format(draft['id'], draft['message']))
    except errors.HttpError, error:
        print('An error has occured: {}'.format(error))
        return error


def delete_draft(draftid):
    service = get_service()
    user_id = get_user_id()
    try:
        service.users().drafts().delete(userId=user_id, id=draftid).execute()
        print('Draft with id: {} deleted successfully'.format(draftid))
    except errors.HttpError, error:
        print('An error has occured: {}'.format(error))
        return error
