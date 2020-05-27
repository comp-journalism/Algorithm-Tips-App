from google.oauth2 import id_token
from werkzeug.exceptions import BadRequest
from google.auth.transport import requests
from api.db import engine
from api.models import users
from sqlalchemy.sql import select, and_
from flask import request, abort, Blueprint, session
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

    return idinfo


def signup(token):
    """Validates the given token, and then adds them to the users table if
    validation succeeds. Returns the INTERNAL user id on success. Otherwise, None."""
    info = validate_token(token)

    if info is None:
        return None

    with engine().connect() as con:
        email = info['email'] if info['email_verified'] else None

        query = select([users.c.id]).where(
            and_(users.c.external_id == info['sub'], users.c.external_type == 'GOOGLE'))

        res = con.execute(query)

        if res.rowcount >= 1:
            row = res.fetchone()
            return row[0]
        else:
            res = con.execute(users.insert().values(
                external_id=info['sub'], external_type='GOOGLE', email=email))
            return res.inserted_primary_key[0]


def parse_token():
    try:
        body = request.get_json()
        return body['id_token']
    except (BadRequest, KeyError, TypeError):
        # body is not json or no id_token key
        return None


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'id' not in session:
            return abort(401)
        return view(uid=session['id'], **kwargs)

    return wrapped_view


def login_used(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        return view(uid=session.get('id', None), **kwargs)
    return wrapped_view


auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/signin', methods=('POST',))
def signin():
    token = parse_token()
    if token is None:
        # no token present
        return abort(400)

    internal_id = signup(token)

    if internal_id is None:
        # invalid token
        return abort(401)

    # flask uses the secret key to sign session contents. users cannot modify
    # the session unless they also possess the secret key
    session['id'] = internal_id

    return {'status': 'ok'}


@auth.route('/signout')
def signout():
    session.pop('id', None)
    return {'status': 'ok'}
