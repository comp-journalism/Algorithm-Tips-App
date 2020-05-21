from google.oauth2 import id_token
from werkzeug.exceptions import BadRequest
from google.auth.transport import requests
from api.db import make_connection, release_connection
from flask import request, abort
from pymysql.cursors import DictCursor
from functools import wraps

# TODO: move to credentials file. same with frontend
CLIENT_ID = "741161465779-iarif5gv7i2shgk80gmleg1trdtpb4hp.apps.googleusercontent.com"


def validate_token(token):
    """validates a token received from the client against Google's servers. on
    success, returns the EXTERNAL user id. on failure, returns None."""
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), CLIENT_ID)
    except ValueError as e:
        print(e)
        return None

    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        return None

    return idinfo['sub']


def signup(token):
    """Validates the given token, and then adds them to the users table if
    validation succeeds. Returns the INTERNAL user id on success. Otherwise, None."""
    uid = validate_token(token)

    if uid is None:
        return None

    con = make_connection()
    try:
        cur = con.cursor(DictCursor)

        cur.execute(
            'insert into users (external_id, external_type) values (%s, %s) on duplicate key update id = id;',
            (uid, 'GOOGLE'))

        # cannot use last_insert_id() because we may not actually insert anything
        cur.execute(
            'select id from users where external_id = %s and external_type = %s',
            (uid, 'GOOGLE')
        )

        result = cur.fetchone()

        return result['id']
    finally:
        release_connection(con)


def parse_token():
    try:
        body = request.get_json()
        return body['id_token']
    except (BadRequest, KeyError):
        # body is not json or no id_token key
        return None


def token_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        token = parse_token()
        if token is None:
            return abort(400)

        uid = signup(token)
        if uid is None:
            return abort(401)

        return view(uid=uid, **kwargs)

    return wrapped_view
