from __future__ import print_function

from flask import session, request, render_template, jsonify
from inboxbird import app



@app.route('/new-compose')
def new_compose():
    print("new compose window")
    return jsonify({'success': 'new compose true'})


@app.route('/on-send')
def on_send():
    print("on send message")
    return jsonify({'success': 'on send true'})


@app.route('/body-changed')
def body_changed():
    print("Body changed")
    return jsonify({'success': 'body changed true'})
