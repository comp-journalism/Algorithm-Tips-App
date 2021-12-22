from configparser import ConfigParser
from datetime import datetime, timedelta
from urllib.parse import quote as urlencode

import boto3
from flask import current_app, render_template
from itsdangerous import URLSafeTimedSerializer, URLSafeSerializer
from sqlalchemy.sql import and_, select

from api.errors import ConfirmationPendingError
from api.models import pending_confirmations, confirmed_emails

CHARSET = 'UTF-8'
BASE_URL = 'https://db.algorithmtips.org'


class MailSingleton:
    __mail = None
    __sender = None

    @classmethod
    def init(cls):
        config = ConfigParser()
        config.read('keys.conf')

        region = config.get('mail', 'ses-region')
        aws_access_key_id = config.get('mail', 'ses-access-key-id')
        aws_secret_access_key = config.get('mail', 'ses-secret-access-key')

        cls.__mail = boto3.client('ses', region_name=region,
                                  aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        cls.__sender = config.get('mail', 'sender-address')

    @classmethod
    def get_mailer(cls):
        assert cls.__mail is not None
        return cls.__mail

    @classmethod
    def get_sender(cls):
        assert cls.__sender is not None
        return cls.__sender


def init_mail():
    MailSingleton.init()


def render_confirmation_email(confirmation_id):
    signer = URLSafeTimedSerializer(current_app.secret_key)
    link = f"https://db.algorithmtips.org/confirm-email?token={signer.dumps(confirmation_id, salt='confirm')}"

    html = render_template('confirmation.html', link=link)
    text = render_template('confirmation.txt', link=link)

    return (html, text)


def send_confirmation(uid, email, con, min_delay=timedelta(days=1)):
    """Sends a confirmation email via Flask-Mail, then records the pending
    confirmation in the database to prevent spamming a recipient with
    confirmation emails."""
    # is this email already confirmed?
    query = select([confirmed_emails]).where(and_(confirmed_emails.c.user_id == uid, confirmed_emails.c.email == email))
    res = con.execute(query).fetchone()

    if res is not None:
        return False

    # does this email have a recent pending confirmation?
    min_date = datetime.now() - min_delay
    query = select([pending_confirmations]).where(and_(
        pending_confirmations.c.email == email, pending_confirmations.c.send_date >= min_date))
    res = con.execute(query)

    if res.rowcount > 0:
        raise ConfirmationPendingError(
            'The most recent confirmation was sent too recently. Please wait a few minutes and try again.')

    res = con.execute(pending_confirmations.insert().values(  # pylint: disable=no-value-for-parameter
        user_id=uid,
        email=email,
        send_date=datetime.now()
    ))

    confirmation_id = res.inserted_primary_key[0]

    (html_body, text_body) = render_confirmation_email(confirmation_id)

    # send a confirmation mail
    try:
        mail = MailSingleton.get_mailer()
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
            Source=MailSingleton.get_sender()
        )
    except Exception as e:
        print(e)
        return False
    else:
        print('sent confirmation email to ' + email)
        return True


def format_source(alert):
    KEYS = ['federal_source', 'regional_source', 'local_source']
    result = []
    any_count = 0
    for key in KEYS:
        display_key = key.split('_')[0].capitalize()
        if key not in alert or alert[key] is None:
            result += ['Any ' + display_key]
            any_count += 1
        elif alert[key] == 'exclude':
            result += ['No ' + display_key]
        else:
            result += [alert[key]]

    if any_count == len(KEYS):
        return None
    else:
        return ', '.join(result)


def build_db_url(alert):
    from api.alerts import min_date_threshold
    KEYS = {
        'filter': 'filter',
        'federal_source': 'federal',
        'regional_source': 'regional',
        'local_source': 'local'
    }

    min_date = min_date_threshold(alert['frequency']).strftime('%Y-%m-%d')
    max_date = datetime.now().strftime('%Y-%m-%d')

    input_params = [f'{value}={urlencode(alert[key])}' for key, value in KEYS.items() if key in alert and alert[key]]
    input_params += [f'from={min_date}', f'to={max_date}']

    params = '&'.join(input_params)
    if params:
        return f"{BASE_URL}/db?{params}"
    else:
        return f"{BASE_URL}/db"


def get_private_alert_token(uid, send_id):
    signer = URLSafeSerializer(current_app.secret_key)
    return signer.dumps({
        'user': uid,
        'send': send_id,
    }, salt='private_alert_token')


def read_private_alert_token(token):
    signer = URLSafeSerializer(current_app.secret_key)
    return signer.loads(token, salt='private_alert_token')


def render_alert(alert, leads):
    private_token = get_private_alert_token(alert['user_id'], alert['send_id'])
    kwargs = {
        'filter_text': alert['filter'],
        'source_text': format_source(alert),
        'leads': leads,
        'links': {
            'alert': build_db_url(alert),
            'delete': f"{BASE_URL}/delete-alert?token={private_token}",
            'unsubscribe': f"{BASE_URL}/unsubscribe?token={private_token}",
        }
    }
    html = render_template('alert.html', **kwargs)
    text = render_template('alert.txt', **kwargs)

    return (html, text)


def send_alert(alert, html_content, text_content):
    try:
        mail = MailSingleton.get_mailer()
        mail.send_email(
            Destination={
                'ToAddresses': [alert['recipient']]
            },
            Message={
                'Subject': {
                    'Charset': CHARSET,
                    'Data': 'Algorithm Tips: New Leads Match Your Alert'
                },
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': text_content,
                    },
                    'Html': {
                        'Charset': CHARSET,
                        'Data': html_content,
                    }
                }
            },
            Source=MailSingleton.get_sender()
        )
    except Exception as e:
        print(e)
        return False
    else:
        print('sent alert email to ' + alert['recipient'])
        return True
