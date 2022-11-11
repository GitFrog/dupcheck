import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
import smtplib
from email.message import EmailMessage
import sys
import apiEngine as API

def log(s, createLog, sendEmail, stopScript, emailGroup=""):
    dirProb = "//cysbigdcdbmsq06/Data/Data Sharing/Accerta/"
    dirLogFile = dirProb + "Logs/"
    if createLog:
        with open(dirLogFile + "_PYTHON_DUPCHECK_LOG.txt", 'a') as f:
            f.write(s + "\n")
    if sendEmail:
        api = API.api()
        api.post(s, emailGroup)
    if stopScript:
        sys.exit()

def sendGmail(s):
    email_address = "oap.error.notification@gmail.com"
    email_password = "oapnotification2022"

    # create email
    msg = EmailMessage()
    msg['Subject'] = "OAP Duplication Check Error"
    msg['From'] = email_address
    msg['To'] = "lee.hulsesmith@ontario.ca"
    msg.set_content(s)

    # send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)


def sendSendGrid(s):
    message = Mail(
        from_email='oap.error.notification@gmail.com',
        to_emails='lee.hulsesmith@ontario.ca',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>' + s + '</strong>')
    #try:
    sg = SendGridAPIClient(os.environ.get('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'))
    response = sg.send(message)
        #print(response.status_code)
        #print(response.body)
        #print(response.headers)
    #except Exception as e:
        #print(e.message)