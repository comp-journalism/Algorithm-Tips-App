import flask
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, select, text

from api.auth import login_required
from api.db import engine
from api.models import flags as flags_
from api.models import leads

flags = Blueprint('flags', __name__, url_prefix='/flag')


@flags.route('/list', methods=('POST',))
@login_required
def list_flags(uid):
    """Receives a list of ids as JSON in the message body. Returns a list of flags (True/False) for each id."""
    try:
        ids = request.get_json()

        if not isinstance(ids, list):
            raise ValueError()
    except ValueError:
        flask.abort(400)

    if len(ids) == 0:
        return {'flags': []}

    with engine().begin() as con:
        uflags = select([flags_.c.id, flags_.c.lead_id])\
            .where(flags_.c.user_id == uid).alias('uflags')

        query = select([leads.c.id, text('not isnull(uflags.id) as flagged')])\
            .select_from(leads.outerjoin(uflags))\
            .where(leads.c.id.in_(ids))

        res = con.execute(query)

        result = {row['id']: row['flagged'] for row in res}

        return {'flags': [result[id] if id in result else False for id in ids]}


@flags.route('/<lead_id>', methods=('PUT',))
@login_required
def put_flag(uid, lead_id):
    with engine().begin() as con:
        query = flags_.insert().values(  # pylint: disable=no-value-for-parameter
            lead_id=lead_id, user_id=uid)

        try:
            res = con.execute(query)
            return {'status': 'ok', 'rows': res.rowcount}
        except IntegrityError:
            # invalid lead_id
            return flask.abort(404)


@flags.route('/<lead_id>', methods=('DELETE',))
@login_required
def delete_flag(uid, lead_id):
    with engine().begin() as con:
        query = flags_.delete().where(  # pylint: disable=no-value-for-parameter
            and_(flags_.c.lead_id == lead_id, flags_.c.user_id == uid))
        res = con.execute(query)
        return {'status': 'ok', 'rows': res.rowcount}
