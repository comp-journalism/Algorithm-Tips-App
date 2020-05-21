import flask
from flask import Blueprint, request
from api.db import make_connection, release_connection
from api.auth import token_required
from pymysql.cursors import DictCursor
from pymysql.err import IntegrityError

flags = Blueprint('flags', __name__, url_prefix='/flag')

# listing flags is done in api.py


@flags.route('/<lead_id>', methods=('PUT',))
@token_required
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
@token_required
def delete_flag(uid, lead_id):
    con = make_connection()
    try:
        cur = con.cursor()
        count = cur.execute(
            'delete from flags where lead_id = %s and user_id = %s;', (lead_id, uid))
        return {'status': 'ok', 'rows': count}
    finally:
        release_connection(con)
