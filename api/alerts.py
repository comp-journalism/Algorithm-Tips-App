import re
from configparser import ConfigParser
from datetime import datetime, timedelta
from itertools import islice
from itsdangerous import BadSignature

import flask
from flask import Blueprint, current_app, request
from sqlalchemy.sql import and_, func, not_, select, tuple_

from api.auth import login_required
from api.db import engine
from api.errors import ConfirmationPendingError, abort_json
from api.mail import send_confirmation, render_alert, BASE_URL, send_alert, read_private_alert_token
from api.models import alerts as alerts_
from api.models import (annotated_leads, confirmed_emails, leads,
                        sent_alert_contents, sent_alerts, users)

alerts = Blueprint('alerts', __name__, url_prefix="/alert")

CONFIRMATION_NOTE = 'You will not receive alerts until your email has been confirmed. You should receive a confirmation email momentarily. Follow the instructions within to confirm your address.'


def init_alerts():
    cfg = ConfigParser()
    cfg.read('keys.conf')

    current_app.config['ALERT_TRIGGER_WHITELIST'] = cfg.get(
        'alert-trigger', 'trigger_ip_whitelist').split(',')


def is_confirmed(uid, emails, con):
    """Checks if an email or emails has been confirmed."""
    if isinstance(emails, list):
        res = con.execute(select([confirmed_emails]).where(
            and_(confirmed_emails.c.user_id == uid, confirmed_emails.c.email.in_(emails))))
        confirmed = {email: False for email in emails}
        for row in res:
            confirmed[row['email']] = True

        return confirmed
    else:
        res = con.execute(select([confirmed_emails]).where(
            and_(confirmed_emails.c.user_id == uid, confirmed_emails.c.email == emails)))

        return res.rowcount >= 1


def format_alert(row):
    return {
        'sources': {
            'federal': row['federal_source'],
            'regional': row['regional_source'],
            'local': row['local_source']
        },
        **{k: v for k, v in row.items() if not k.endswith('_source')}
    }


@alerts.route('/<alert_id>', methods=('GET',))
@login_required
def lookup_alert(uid, alert_id):
    with engine().begin() as con:
        query = select([alerts_])\
            .where(and_(alerts_.c.id == alert_id, alerts_.c.user_id == uid))
        res = con.execute(query)
        if res.rowcount == 0:
            # does not exist or no access
            return flask.abort(404)

        response = format_alert(res.fetchone())
        response['confirmed'] = is_confirmed(uid, response['recipient'], con)
        return flask.jsonify(response)


@alerts.route('/<alert_id>', methods=('PUT',))
@login_required
def update_alert(uid, alert_id):
    try:
        data = request.get_json()
        assert EMAIL_REGEX.fullmatch(data['recipient']) is not None
    except AssertionError:
        return flask.abort(400, {
            'status': 'error',
            'reason': 'Unable to read or validate alert data'
        })

    with engine().begin() as con:
        query = alerts_.update().values(  # pylint: disable=no-value-for-parameter
            filter=data['filter'],
            recipient=data['recipient'],
            federal_source=data['sources'].get('federal', None),
            regional_source=data['sources'].get('regional', None),
            local_source=data['sources'].get('local', None),
            frequency=data['frequency']
        ).where(and_(alerts_.c.id == alert_id, alerts_.c.user_id == uid))

        res = con.execute(query)

        if res.rowcount == 0:
            return flask.abort(404)

        try:
            conf_sent = send_confirmation(uid, data['recipient'], con)
        except ConfirmationPendingError:
            # confirmation email already pending
            return {'status': 'ok', 'notes': ['A confirmation email is pending.']}

        if conf_sent:
            return {'status': 'ok', 'notes': [CONFIRMATION_NOTE]}
        else:
            return {'status': 'ok'}


@alerts.route('/<alert_id>', methods=('DELETE',))
@login_required
def delete_alert(uid, alert_id):
    with engine().begin() as con:
        query = alerts_.delete().where(  # pylint: disable=no-value-for-parameter
            and_(alerts_.c.id == alert_id, alerts_.c.user_id == uid))
        res = con.execute(query)
        if res.rowcount == 0:
            return flask.abort(404)

        return {'status': 'ok'}


@alerts.route('/delete')
def delete_alert_via_link():
    token = request.args.get('token', None)
    if token is None:
        return abort_json(400, 'Missing token')

    try:
        contents = read_private_alert_token(token)
        with engine().begin() as con:
            send_query = sent_alerts.select().where(and_(sent_alerts.c.id == contents['send'], sent_alerts.c.user_id == contents['user']))
            res = con.execute(send_query)
            sent = res.fetchone()
            # test (sqlite) database doesn't support CTEs on DELETEs so rather
            # than have this untested we're just going to use 2 queries. this
            # endpoint shouldn't be hit often so this cost should be low
            query = alerts_.delete().where(alerts_.c.id == sent['alert_id'])
            res = con.execute(query)

            if res.rowcount == 0:
                return abort_json(404, 'No such alert')
    except BadSignature:
        return abort_json(400, 'Invalid token')
    return {'status': 'ok'}


@alerts.route('/unsubscribe')
def unsubscribe_all_alerts():
    token = request.args.get('token', None)
    if token is None:
        return abort_json(400, 'Missing token')

    try:
        contents = read_private_alert_token(token)
        with engine().begin() as con:
            send_query = sent_alerts.select().where(and_(sent_alerts.c.id == contents['send'], sent_alerts.c.user_id == contents['user']))
            res = con.execute(send_query)
            sent = res.fetchone()

            # see note in delete_alert_via_link
            query = confirmed_emails.delete().where(confirmed_emails.c.email == sent['recipient'])
            res = con.execute(query)
            query = alerts_.delete().where(alerts_.c.recipient == sent['recipient'])
            res = con.execute(query)

            if res.rowcount == 0:
                return abort_json(404, 'No such alert')
    except BadSignature:
        return abort_json(400, 'Invalid token')
    return {'status': 'ok'}


@alerts.route('/list', methods=('GET',))
@login_required
def list_alerts(uid):
    with engine().begin() as con:
        query = select([alerts_])\
            .where(alerts_.c.user_id == uid)
        res = con.execute(query)
        if res.rowcount == 0:
            return {'alerts': []}

        results = res.fetchall()
        alert_list = [format_alert(r) for r in results]

        confirmed = is_confirmed(uid, [alert['recipient']
                                       for alert in alert_list], con)

        for alert in alert_list:
            alert['confirmed'] = confirmed[alert['recipient']]
        return {'alerts': alert_list}


EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


@alerts.route('/create', methods=('POST',))
@login_required
def create_alert(uid):
    try:
        data = request.get_json()
        assert EMAIL_REGEX.fullmatch(data['recipient']) is not None
    except AssertionError:
        return abort_json(400, 'Unable to read or validate alert data')

    with engine().begin() as con:
        # before beginning, check if this email belongs to another existing users
        query = select([users]).where(
            and_(users.c.email == data['recipient'], not_(users.c.id == uid)))
        res = con.execute(query)

        if res.rowcount > 0:
            return flask.abort(400, {
                'status': 'error',
                'reason': 'Email address is already claimed by another users.'
            })

        query = select([confirmed_emails]).where(and_(
            confirmed_emails.c.email == data['recipient'], not_(confirmed_emails.c.user_id == uid)))
        res = con.execute(query)

        if res.rowcount > 0:
            return flask.abort(400, {
                'status': 'error',
                'reason': 'Email address is already claimed by another users.'
            })

        # we're going to abuse the DB to do validation & type checking. the only exception is the email, which is validated above
        try:
            query = alerts_.insert().values(  # pylint: disable=no-value-for-parameter
                filter=data['filter'],
                recipient=data['recipient'],
                federal_source=data['sources'].get('federal', None),
                regional_source=data['sources'].get('regional', None),
                local_source=data['sources'].get('local', None),
                frequency=data['frequency'],
                user_id=uid
            )

            res = con.execute(query)

            assert len(res.inserted_primary_key) > 0

            alert_id = res.inserted_primary_key[0]
        except Exception as e:
            print(e)
            return flask.abort(400, {
                'status': 'error',
                'reason': 'Unable to create alert in database'
            })

        base = {'id': alert_id}
        try:
            conf_sent = send_confirmation(uid, data['recipient'], con)
        except ConfirmationPendingError:
            return {'notes': ['A confirmation for this recipient is already pending.'], **base}
        else:
            if conf_sent:
                return {'status': 'ok', 'notes': [CONFIRMATION_NOTE], **base}
            else:
                return {'status': 'ok', **base}


@alerts.route('/<alert_id>/resend-confirmation')
@login_required
def resend_confirmation(alert_id, uid):
    with engine().begin() as con:
        query = select([alerts_]).where(
            and_(alerts_.c.id == alert_id, alerts_.c.user_id == uid))
        res = con.execute(query)

        if res.rowcount == 0:
            return abort_json(400, 'This email address is already confirmed.')

        alert = res.fetchone()

        try:
            send_confirmation(
                uid, alert['recipient'], con, min_delay=timedelta(minutes=5))
        except ConfirmationPendingError as err:
            return abort_json(400, err.message)
        else:
            return {'status': 'ok'}


def min_date_threshold(kind, fudge=timedelta(hours=6)):
    """Calculate the minimum date threshold for each frequency type.

    `fudge` gives a small error margin (default: 6 hours) to cope with clock and/or cron skew."""
    if kind == 0:
        return datetime.now() - timedelta(weeks=1) + fudge
    elif kind == 1:
        return datetime.now() - timedelta(days=10) + fudge
    elif kind == 2:
        return datetime.now() - timedelta(days=30) + fudge


@alerts.route('/trigger', methods=('POST',))
def trigger_alerts():
    from api.api import build_filtered_lead_selection
    if request.remote_addr not in current_app.config['ALERT_TRIGGER_WHITELIST']:
        return abort_json(401, 'Unauthorized')

    with engine().connect() as con:
        # select all alerts where:
        # 1. the recipient email is confirmed
        # 2. the alert hasn't been sent in the current time period
        confirmed = select(
            [confirmed_emails.c.user_id, confirmed_emails.c.email]).cte()
        query = select([alerts_, func.max(sent_alerts.c.send_date).label('last_sent')])\
            .select_from(alerts_.outerjoin(sent_alerts, sent_alerts.c.alert_id == alerts_.c.id))\
            .where(tuple_(alerts_.c.user_id, alerts_.c.recipient).in_(confirmed))\
            .group_by(alerts_.c.id)

        results = con.execute(query)

        # these results satisfy #1, but not #2 yet
        # however, we need to go row by row anyway because MySQL cannot match
        # on column values (only plaintext)
        for result in results:
            row = dict(result)
            if row['last_sent'] is not None and row['last_sent'] >= min_date_threshold(row['frequency']):
                # has been sent more recently than we allow
                print(
                    f"Last trigger for {row['id']} is too recent ({row['last_sent']}, {min_date_threshold(row['frequency'])})")
                continue
            with con.begin():
                query = build_filtered_lead_selection(
                    filter_=row['filter'],
                    from_=None,
                    to=None,
                    sources={
                        key: row[f"{key}_source"]
                        for key in ['federal', 'regional', 'local']
                    },
                    page=None,
                    fields=[leads.c.id, annotated_leads.c.name],
                    where=[
                        annotated_leads.c.published_dt >= min_date_threshold(
                            row['frequency'], fudge=timedelta(0))
                    ]
                )

                lead_results = con.execute(query)
                lead_results = list(dict(row) for row in lead_results)

                if len(lead_results) == 0:
                    print(f"Skipping alert {row['id']}. No new results.")
                    continue

                # record alert sending
                sent_alert = {
                    k: v
                    for k, v in row.items()
                    if k not in ['id', 'last_sent']
                }

                sent_alert['alert_id'] = row['id']
                sent_alert['send_date'] = datetime.now()

                query = sent_alerts.insert().values(  # pylint: disable=no-value-for-parameter
                    **sent_alert)

                res = con.execute(query)

                send_id = res.inserted_primary_key[0]

                sent_alert['send_id'] = send_id

                templates = render_alert(sent_alert, [{
                    'name': lead['name'],
                    'link': f'{BASE_URL}/lead/{lead["id"]}'
                } for lead in islice(lead_results, 3)])

                sent_contents = [
                    {'send_id': send_id,
                     'lead_id': lead['id']}
                    for lead in lead_results
                ]

                con.execute(sent_alert_contents.insert(  # pylint: disable=no-value-for-parameter
                ), *sent_contents)

                send_alert(sent_alert, *templates)

    return {'status': 'ok'}
