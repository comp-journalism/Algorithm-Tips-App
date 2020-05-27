from flask import current_app
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from configparser import ConfigParser
from api.models import pending_confirmations, users
from sqlalchemy.sql import select, and_, not_
from datetime import datetime, timedelta

mail = Mail()


def init_mail(app):
    """Set up flask-mail with settings from keys.conf"""
    config = ConfigParser()
    config.read('keys.conf')

    app.config['MAIL_SERVER'] = config.get('flask-mail', 'server')
    app.config['MAIL_USE_TLS'] = config.getboolean('flask-mail', 'tls')
    app.config['MAIL_USE_SSL'] = config.getboolean('flask-mail', 'ssl')
    app.config['MAIL_PORT'] = config.get('flask-mail', 'port')
    app.config['MAIL_USERNAME'] = config.get('flask-mail', 'username')
    app.config['MAIL_PASSWORD'] = config.get('flask-mail', 'password')
    app.config['MAIL_DEFAULT_SENDER'] = config.get('flask-mail', 'sender')

    return mail.init_app(app)


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
        pending_confirmations.c.email == email, pending_confirmations.c.send_date <= min_date))
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

    # send a confirmation mail
    msg = Message('Algorithm Tips: Confirm Your Email',
                  recipients=[email])
    msg.body = f"""An alert was created with this email address on the Algorithm Tips (http://algorithmtips.org) website.

    If you took this action, click here to confirm your email address: {link}
    
    If you did not, simply ignore this email.
    """

    msg.html = f"""<p>An alert was created with this email address on the <a href="http://algorithmtips.org">Algorithm Tips</a> website.

    <p>If you took this action, click <a href="{link}">here</a> to confirm your email address.</p>

    <p>If you did not, simply ignore this email.</p>
    """

    mail.send(msg)

    return True
