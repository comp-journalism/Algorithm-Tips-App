import re
import flask
from flask import Blueprint, request
from sqlalchemy.sql import select, and_, text
from api.db import engine
from api.models import alerts as alerts_, users
from api.auth import login_required

alerts = Blueprint('alerts', __name__, url_prefix="/alert")


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
    with engine().connect() as con:
        query = select([alerts_, text('recipient = users.email as confirmed')])\
            .select_from(alerts_.join(users))\
            .where(and_(alerts_.c.id == alert_id, users.c.id == uid))
        res = con.execute(query)
        if res.rowcount == 0:
            # does not exist or no access
            return flask.abort(404)

        return flask.jsonify(format_alert(res.fetchone()))


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
            federal_source=data['sources'].get('federal', None),
            regional_source=data['sources'].get('regional', None),
            local_source=data['sources'].get('local', None),
            frequency=data['frequency']
        ).where(and_(alerts_.c.id == alert_id, alerts_.c.user_id == uid))

        res = con.execute(query)

        if res.rowcount == 0:
            return flask.abort(404)

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
        return {'alerts': [format_alert(r) for r in results]}


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

            return {'id': res.inserted_primary_key[0]}
        except Exception as e:
            print(e)
            return flask.abort(400, {
                'status': 'error',
                'reason': 'Unable to create alert in database'
            })
