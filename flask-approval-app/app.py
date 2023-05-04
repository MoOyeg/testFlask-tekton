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

def onfailure_update_disk():
    '''Update Disk with Failure'''
    with open('/memory-storage/approvaldecision', 'w') as f:
        f.write("Error")
        
@app.route("/")
def home():
    logger.info("Home Page Accessed")
    form = PostForm()
    try:        
        form.pipelinerun=os.environ.get('PIPELINE_RUN_NAME') or "Unknown"
        form.approval_cmd=os.environ.get('PROMOTE_COMMAND') or "Unknown"
    except Exception as e:
        logger.error("Error getting $PIPELINE_RUN_NAME or $PROMOTE_COMMAND from environment will exit %s",e)
        onfailure_update_disk()
        
    try:
       form.authorized_user=request.authorization.username
    except:
        logger.error("Error getting authorized username from Oauth Proxy %s",e)
        onfailure_update_disk()    
    
    logger.info("Approval Requested for Pipeline Run Name: %s",form.pipelinerun)
    return render_template('approval.html', postform=form)


@app.route("/approval_status",methods=['POST'])
def approval_status():
    '''Get Approval Status and Update Disk'''
    
    if request.method == 'POST':
        approval_string=""
        if request.form['submit_button'] == 'Approve':
            logger.info("Approval Provided for Pipeline Run Name: %s",request.form['pipelinerun'])
            try:
                approval_string=os.environ.get('uniqueapprovedstring')
            except Exception as e:
                logger.error("Error getting uniqueapprovedstring info from environment - will exit %s",e)
                onfailure_update_disk()
            with open('/memory-storage/approvaldecision', 'w') as f:
                f.write(approval_string)
            return "Will Approve Pipeline Run"
        
        elif request.form['submit_button'] == 'Disapprove':
            logger.info("Disapproval Provided for Pipeline Run Name: %s",request.form['pipelinerun'])
            try:
                logger.debug("Get Denied String from Disk")
                with open('/memory-storage/appcookiesecret', 'r') as f:
                    disapproval_string = f.read()                
            except Exception as e:
                logger.error("Error getting uniquedeniedstring info from environment - will exit %s",e)
                onfailure_update_disk()
            with open('/memory-storage/approvaldecision', 'w') as f:
                f.write(disapproval_string)
            return "Will Dissaprove Pipeline Run"
        
    if approval_string == "" or approval_string == None:
        logger.error("Error getting approval string or denied string from environment - will exit")
    onfailure_update_disk()                   
    return "Promotion Process has Failed, will end Pipeline Run"

if __name__ == '__main__':
    logger.info("Starting Approval App")
    
    try:
        logger.info("Get Flask Secret Key")
        with open('/memory-storage/appcookiesecret', 'r') as f:
            app.config['SECRET_KEY'] = f.read()        
    except Exception as e:
        logger.error("Could not get App Cookie Secret from environment - will exit %s",e)
        onfailure_update_disk()
        
    try:
        logger.info("Get Flask Port")
        port=os.environ.get('OAUTH_APPROVER_PORT')
        app.run(host='127.0.0.1', port=port, debug=True)
    except Exception as e:
        logger.error("Could not get Flask Port from environment - will exit %s",e)
        
        
        