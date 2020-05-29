from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from configparser import ConfigParser
from api.models import pending_confirmations, users
from sqlalchemy.sql import select, and_, not_
from datetime import datetime, timedelta
import boto3

mail = None
CHARSET = 'UTF-8'
SENDER = None


def init_mail():
    """Set up flask-mail with settings from keys.conf"""
    global mail
    global SENDER
    config = ConfigParser()
    config.read('keys.conf')

    region = config.get('mail', 'ses-region')
    aws_access_key_id = config.get('mail', 'ses-access-key-id')
    aws_secret_access_key = config.get('mail', 'ses-secret-access-key')

    mail = boto3.client('ses', region_name=region,
                        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    SENDER = config.get('mail', 'sender-address')


def send_confirmation(uid, email, con):
    """Sends a confirmation email via Flask-Mail, then records the pending
    confirmation in the database to prevent spamming a recipient with
    confirmation emails."""
    # is this the google account's email?
    query = select([users.c.email]).where(
        and_(users.c.id == uid, users.c.email == email))
    res = con.execute(query)

    if res.rowcount == 1:
        return False  # no email sent

    # does this email have a recent pending confirmation?
    min_date = datetime.now() - timedelta(days=1)
    query = select([pending_confirmations]).where(and_(
        pending_confirmations.c.email == email, pending_confirmations.c.send_date >= min_date))
    res = con.execute(query)

    if res.rowcount > 0:
        return False  # no email sent

    res = con.execute(pending_confirmations.insert().values(  # pylint: disable=no-value-for-parameter
        user_id=uid,
        email=email,
        send_date=datetime.now()
    ))

    confirmation_id = res.inserted_primary_key[0]

    signer = URLSafeTimedSerializer(current_app.secret_key)
    link = f"http://db.algorithmtips.org/confirm-email?token={signer.dumps(confirmation_id, salt='confirm')}"

    print(link)

    text_body = f"""An alert was created with this email address on the Algorithm Tips (http://algorithmtips.org) website.

    If you took this action, click here to confirm your email address: {link}
    
    If you did not, simply ignore this email.
    """

    html_body = f"""<p>An alert was created with this email address on the <a href="http://algorithmtips.org">Algorithm Tips</a> website.

    <p>If you took this action, click <a href="{link}">here</a> to confirm your email address.</p>

    <p>If you did not, simply ignore this email.</p>
    """

    # send a confirmation mail
    try:
        mail.send_email(
            Destination={
                'ToAddresses': [email]
            },
            Message={
                'Subject': {
                    'Charset': CHARSET,
                    'Data': 'Algorithm Tips: Confirm Your Email'
                },
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': text_body
                    },
                    'Html': {
                        'Charset': CHARSET,
                        'Data': html_body,
                    }
                }
            },
            Source=SENDER
        )
    except Exception as e:
        print(e)
        print(e.response['Error']['Message'])
        return False
    else:
        print('sent confirmation email to ' + email)
        return True
