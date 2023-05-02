import re
from datetime import datetime
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, make_response, has_app_context,Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
import os
import logging

app = Flask(__name__)
app.secret_key = 'test'

class PostForm(FlaskForm):
    '''Set Form to be used fields'''
    pipelinerun = StringField('pipelinerun')
    approval_cmd= StringField('approval_cmd')
    approve = SubmitField('submit')
    disapprove = SubmitField('disapprove')

@app.route("/")
def home():
    form = PostForm()
    form.pipelinerun=os.environ.get('PIPELINE_RUN_NAME') or "Unknown"
    form.approval_cmd=os.environ.get('APPROVAL_CMD') or "Unknown"
    return render_template('approval.html', postform=form)


@app.route("/hello/<name>")
def hello_there(name):
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")

    # Filter the name argument to letters only using regular expressions. URL arguments
    # can contain arbitrary text, so we restrict to safe characters only.
    match_object = re.match("[a-zA-Z]+", name)

    if match_object:
        clean_name = match_object.group(0)
    else:
        clean_name = "Friend"

    content = "Hello there, " + clean_name + "! It's " + formatted_now
    return content