import os
import smtplib
from flask import url_for
from flaskalbum import app


# Function to send a password reset email to the user
def send_reset_email(user):
    EMAIL_ID = os.getenv('EMAIL_ID')
    EMAIL_PASS = os.getenv('EMAIL_PASS')
    # Generate a password reset token and construct the reset email content
    token = user.get_reset_token()
    
    
    # Email configuration and content
    email_user = EMAIL_ID
    email_pwd = EMAIL_PASS

    TO = [user.email]
    SUBJECT = "Password Reset Request"
    TEXT = f'''
To reset your password, visit the following link:

{url_for('reset_token', token=token, _external=True)}

This link is valid for 10 minutes.
If you did not make this request, then simply ignore this email and no changes will be made.

Regards
Aansh Ojha
'''
    server = smtplib.SMTP('smtp.zoho.in', 587)
    server.ehlo()
    server.starttls()
    server.login(email_user, email_pwd)
    BODY = '\r\n'.join(['To: %s' % TO,
            'From: %s' % email_user,
            'Subject: %s' % SUBJECT,
            '', TEXT])
    
    # Send the email using SMTP
    server.sendmail(email_user, [TO], BODY)