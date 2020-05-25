import re
import flask
from flask import Blueprint, request
from api.db import connect
from api.auth import login_required
from pymysql.cursors import DictCursor

alerts = Blueprint('alerts', __name__, url_prefix="/alert")


@alerts.route('/<alert_id>', methods=('GET',))
@login_required
def lookup_alert(uid, alert_id):
    with connect() as con, con.cursor(DictCursor) as cur:
        count = cur.execute(
            'select id, filter, recipient, source, frequency from alerts where id = %s and user_id = %s', (alert_id, uid))
        if count == 0:
            # does not exist or no access
            return flask.abort(404)

        return flask.jsonify(cur.fetchone())


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

    with connect() as con, con.cursor(DictCursor) as cur:
        count = cur.execute("""
            update alerts set
                filter = %(filter)s,
                recipient = %(recipient)s,
                source = %(source)s,
                frequency = %(frequency)s
            where id = %(id)s and user_id = %(uid)s;
        """, {**data, 'id': alert_id, 'uid': uid})

        if count == 0:
            return flask.abort(404)

        return {'status': 'ok'}


@alerts.route('/<alert_id>', methods=('DELETE',))
@login_required
def delete_alert(uid, alert_id):
    with connect() as con, con.cursor(DictCursor) as cur:
        count = cur.execute(
            'delete from alerts where id = %s and user_id = %s', (alert_id, uid))
        if count == 0:
            return flask.abort(404)

        return {'status': 'ok'}


@alerts.route('/list', methods=('GET',))
@login_required
def list_alerts(uid):
    with connect() as con, con.cursor(DictCursor) as cur:
        count = cur.execute(
            'select id, filter, recipient, source, frequency from alerts where user_id = %s', (uid,))
        if count == 0:
            return {'alerts': []}

        results = cur.fetchall()
        return {'alerts': results}


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

    with connect() as con, con.cursor(DictCursor) as cur:
        # we're going to abuse the DB to do validation & type checking. the only exception is the email, which is validated above
        try:
            cur.execute("""
                insert into alerts (filter, recipient, source, frequency, user_id) values (%(filter)s, %(recipient)s, %(source)s, %(frequency)s, %(uid)s);
            """, {**data, 'uid': uid})

            cur.execute("select last_insert_id() as id;")

            result = cur.fetchone()
            assert result['id'] > 0

            return {'id': result['id']}
        except:
            return flask.abort(400, {
                'status': 'error',
                'reason': 'Unable to create alert in database'
            })
