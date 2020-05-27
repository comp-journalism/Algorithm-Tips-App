import re
import flask
from datetime import datetime, timedelta
from flask_mail import Message
from flask import Blueprint, request
from sqlalchemy.sql import select, and_, text, not_
from api.db import engine
from api.models import alerts as alerts_, users, pending_confirmations, confirmed_emails
from api.auth import login_required
from api.mail import send_confirmation

alerts = Blueprint('alerts', __name__, url_prefix="/alert")


@alerts.route('/<alert_id>', methods=('GET',))
@login_required
def lookup_alert(uid, alert_id):
    with engine().connect() as con:
        query = select([alerts_, text('recipient = users.email as confirmed')])\
            .select_from(alerts_.join(users))\
            .where(and_(alerts_.c.id == alert_id, users.c.id == uid))
        res = con.execute(query)
        if res.rowcount == 0:
            # does not exist or no access
            return flask.abort(404)

        return flask.jsonify(dict(res.fetchone().items()))


@alerts.route('/<alert_id>', methods=('PUT',))
@login_required
def update_alert(uid, alert_id):
    try:
        data = request.get_json()
        assert EMAIL_REGEX.fullmatch(data['recipient']) is not None
    except:
        return flask.abort(400, {
            'status': 'error',
            'reason': 'Unable to read or validate alert data'
        })

    with engine().connect() as con:
        query = alerts_.update().values(  # pylint: disable=no-value-for-parameter
            filter=data['filter'],
            recipient=data['recipient'],
            source=data['source'],
            frequency=data['frequency']
        ).where(and_(alerts_.c.id == alert_id, alerts_.c.user_id == uid))

        res = con.execute(query)

        if res.rowcount == 0:
            return flask.abort(404)

        send_confirmation(uid, data['recipient'], con)

        return {'status': 'ok'}


@alerts.route('/<alert_id>', methods=('DELETE',))
@login_required
def delete_alert(uid, alert_id):
    with engine().connect() as con:
        query = alerts_.delete().where(  # pylint: disable=no-value-for-parameter
            and_(alerts_.c.id == alert_id, alerts_.c.user_id == uid))
        res = con.execute(query)
        if res.rowcount == 0:
            return flask.abort(404)

        return {'status': 'ok'}


@alerts.route('/list', methods=('GET',))
@login_required
def list_alerts(uid):
    with engine().connect() as con:
        query = select([alerts_, text('recipient = users.email as confirmed')])\
            .select_from(alerts_.join(users))\
            .where(users.c.id == uid)
        res = con.execute(query)
        if res.rowcount == 0:
            return {'alerts': []}

        results = res.fetchall()
        return {'alerts': [dict(r.items()) for r in results]}


EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


@alerts.route('/create', methods=('POST',))
@login_required
def create_alert(uid):
    try:
        data = request.get_json()
        assert EMAIL_REGEX.fullmatch(data['recipient']) is not None
    except:
        return flask.abort(400, {
            'status': 'error',
            'reason': 'Unable to read or validate alert data'
        })

    with engine().connect() as con:
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
                source=data['source'],
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

        send_confirmation(uid, data['recipient'], con)

        return {'id': alert_id}
