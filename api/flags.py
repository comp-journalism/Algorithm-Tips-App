import flask
from flask import Blueprint, request
from api.db import make_connection, release_connection
from api.auth import login_required
from pymysql.cursors import DictCursor
from pymysql.err import IntegrityError

flags = Blueprint('flags', __name__, url_prefix='/flag')


@flags.route('/list', methods=('POST',))
@login_required
def list_flags(uid):
    """Receives a list of ids as JSON in the message body. Returns a list of flags (True/False) for each id."""
    try:
        ids = request.get_json()

        if not isinstance(ids, list):
            raise ValueError()
    except:
        flask.abort(400)

    try:
        con = make_connection()
        cur = con.cursor(DictCursor)
        cur.execute("""
            select leads.id as id, not isnull(uflags.id) as flagged
            from leads
            left join (select id, lead_id from flags where user_id = %(uid)s) as uflags
                on uflags.lead_id = leads.id
            where leads.id in %(ids)s; """, {
            'uid': uid,
            'ids': tuple(ids)
        })

        result = {row['id']: row['flagged'] for row in cur.fetchall()}

        return {'flags': [result[id] if id in result else False for id in ids]}
    finally:
        release_connection(con)


@flags.route('/<lead_id>', methods=('PUT',))
@login_required
def put_flag(uid, lead_id):
    con = make_connection()
    try:
        cur = con.cursor()
        count = cur.execute(
            'insert into flags (lead_id, user_id) values (%s, %s) on duplicate key update id = id;', (lead_id, uid))
        return {'status': 'ok', 'rows': count}
    except IntegrityError:
        # invalid lead_id
        return flask.abort(404)
    finally:
        release_connection(con)


@flags.route('/<lead_id>', methods=('DELETE',))
@login_required
def delete_flag(uid, lead_id):
    con = make_connection()
    try:
        cur = con.cursor()
        count = cur.execute(
            'delete from flags where lead_id = %s and user_id = %s;', (lead_id, uid))
        return {'status': 'ok', 'rows': count}
    finally:
        release_connection(con)
