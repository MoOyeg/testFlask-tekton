import re
from datetime import datetime
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, make_response, has_app_context,Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
import os
import logging
import sys

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class PostForm(FlaskForm):
    '''Set Form to be used fields'''
    authorized_user = StringField('authorized_user')
    pipelinerun = StringField('pipelinerun')
    approval_cmd= StringField('approval_cmd')
    approve = SubmitField('submit')
    disapprove = SubmitField('disapprove')

@app.route("/")
def home():
    logger.info("Home Page Accessed")
    form = PostForm()
    try:
        form.authorized_user=request.authorization.username or "Unknown"
        form.pipelinerun=os.environ.get('PIPELINE_RUN_NAME') or "Unknown"
        form.approval_cmd=os.environ.get('APPROVAL_CMD') or "Unknown"
    except Exception as e:
        logger.error("Error getting $PIPELINE_RUN_NAME or $APPROVAL_CMD from environment will exit %s",e)
        sys.exit(1)
    request.authorization.username
    
    logger.info("Approval Requested for Pipeline Run Name: %s",form.pipelinerun)
    return render_template('approval.html', postform=form)


@app.route("/approval_status",methods=['POST'])
def approval_status():
    if request.method == 'POST':
        approval_string=""
        if request.form['submit_button'] == 'Approve':
            logger.info("Approval Provided for Pipeline Run Name: %s",request.form['pipelinerun'])
            try:
                approval_string=os.environ.get('uniqueapprovedstring')
            except Exception as e:
                logger.error("Error getting uniqueapprovedstring info from environment - will exit %s",e)
                sys.exit(1)
            print(approval_string)
            return "Will Approve Pipeline Run"
        elif request.form['submit_button'] == 'Disapprove':
            logger.info("Disapproval Provided for Pipeline Run Name: %s",request.form['pipelinerun'])
            try:
                disapproval_string=os.environ.get('UNIQUE_DISAPPROVED_STRING_LOCATION') or "/memory-storage/unique_disapproved_string"
            except Exception as e:
                logger.error("Error getting uniquedeniedstring info from environment - will exit %s",e)
                sys.exit(1)
            print(disapproval_string)
            return "Will Dissaprove Pipeline Run"   
        
        if approval_string == "" or approval_string == None:
            logger.error("Error getting approval string or denied string from environment - will exit")
            sys.exit(1)  
    return "Promotion Process has Failed, will end Pipeline Run"

if __name__ == '__main__':
    logger.info("Starting Approval App")
    try:
        logger.info("Get Flask Secret Key")
        app.secret_key=os.environ.get('appcookiesecret')
    except Exception as e:
        logger.error("Could not get App Cookie Secret from environment - will exit %s",e)
    app.run(host='0.0.0.0', port=8080, debug=True)
