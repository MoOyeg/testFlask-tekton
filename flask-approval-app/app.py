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
app.secret_key = 'test'

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
            try:
                approval_string=os.environ.get('INSTANCE_APPROVED_STRING')
            except Exception as e:
                logger.error("Error getting $INSTANCE_APPROVED_STRING from environment will exit %s",e)
                sys.exit(1)
        else:
            try:
                approval_string=os.environ.get('INSTANCE_DISAPPROVED_STRING')
            except Exception as e:
                logger.error("Error getting $INSTANCE_DISAPPROVED_STRING from environment will exit %s",e)
                sys.exit(1)            
        
        if approval_string == "" or approval_string == None:
            logger.error("Error getting $INSTANCE_APPROVED_STRING or $INSTANCE_DISAPPROVED_STRING from environment will exit")
            sys.exit(1)       
        
        workfile = os.environ.get('WORKFILE_LOCATION') or "/memory-storage/workfile"
        try:
            f = open(workfile, 'w+')
            f.write("Approved")
            f.close()
        except Exception as e:
            logger.error("Error writing to workfile %s",e)

    return "test"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)