import configparser
import json
from math import ceil
from os import environ

import flask
from flask import request, Blueprint
from flask_cors import CORS
from sqlalchemy.sql import and_, select, text

from api.alerts import alerts, init_alerts
from api.auth import auth, login_required, login_used
from api.db import engine, init_pool
from api.flags import flags as flags_bp
from api.mail import init_mail
from api.models import annotated_leads, crowd_ratings, flags, leads
from api.errors import abort_json

with open('data/sources.json') as f:
    SOURCES = json.load(f)


def init_keys(app):
    try:
        cfg = configparser.ConfigParser()
        cfg.read('keys.conf')
        app.secret_key = cfg.get('flask', 'session-key')
    except Exception as e:
        print(f'Unable to read keys.conf: {e}. Sessions will be disabled.')


app = flask.Flask(__name__, template_folder="templates")
CORS(app, supports_credentials='DEBUG' in environ)

init_keys(app)

app.register_blueprint(flags_bp)
app.register_blueprint(auth)
app.register_blueprint(alerts)
app.before_first_request(init_mail)
app.before_first_request(init_pool)
app.before_first_request(init_alerts)

main = Blueprint('main', __name__)

LEAD_FIELDS = [
    leads.c.id,
    annotated_leads.c.name,
    annotated_leads.c.description,
    annotated_leads.c.topic,
    annotated_leads.c.published_dt,
    leads.c.discovered_dt,
    leads.c.query_term,
    leads.c.link,
    leads.c.domain,
    leads.c.jurisdiction,
    leads.c.source,
    leads.c.people,
    leads.c.organizations,
    leads.c.document_ext,
    leads.c.document_relevance
]


def build_lead_selection(uid=None, fields=LEAD_FIELDS, where=[], flagged_only=False):
    join = leads.join(annotated_leads)
    if uid is not None:
        fields = fields + [text('not isnull(uflags.id) as flagged')]
        uflags = select([flags.c.id, flags.c.lead_id]).where(
            flags.c.user_id == uid).alias('uflags')

        if flagged_only:
            join = join.join(uflags)
        else:
            join = join.outerjoin(uflags)

    query = select(fields).select_from(join)

    # E712 asks for 'is True' but this is not actually a bool, just bool-y
    return query.where(and_(annotated_leads.c.is_published == True, *where))  # noqa: E712


def build_filtered_lead_selection(filter_, from_, to, sources, page=1, uid=None, fields=LEAD_FIELDS, where=[], flagged_only=False):
    """Build a filtered lead selection query. The filter parameters are required, but the remainder are optional.

    Notes:
    - Setting `page = None` disables pagination.
    - Setting `uid = None` disables the `flagged` field in the output and the corresponding join.
    """
    where = [*where]
    if filter_ is not None and filter_ != '':
        where.append(
            text("(match(name, description, topic) against (:filter in boolean mode) or match(people, organizations) against (:filter in boolean mode))").bindparams(filter=filter_))
    if from_ is not None and from_ != '':
        where.append(annotated_leads.c.published_dt >= from_)
    if to is not None and to != '':
        where.append(annotated_leads.c.published_dt <= to + ' 23:59:59')

    source_values = []
    for key in ['federal', 'regional', 'local']:
        value = sources.get(key, None)
        if value is None:
            source_values += SOURCES[key]
        elif value in SOURCES[key]:
            source_values.append(value)
        else:
            # value is exclude or invalid
            pass

    # if the length of source_values is 0, then this will exclude
    # everything...but that is what the user asked for
    where.append(leads.c.jurisdiction.in_(source_values))

    query = build_lead_selection(
        uid=uid, fields=fields, where=where, flagged_only=flagged_only)

    if page is not None:
        query = query.order_by(annotated_leads.c.published_dt.desc())\
            .limit(PAGE_SIZE).offset(PAGE_SIZE * (page - 1))

    return query


@main.route('/lead/<lead_id>')
@login_used
def get_lead(uid, lead_id):
    with engine().begin() as con:
        query = build_lead_selection(uid, where=[leads.c.id == lead_id])

        resultset = con.execute(query)
        result = resultset.fetchone()
        if result is not None:
            result = dict(result)

            # now we load comments for it
            ratings_query = select([crowd_ratings])\
                .where(crowd_ratings.c.lead_id == lead_id)
            ratings = con.execute(ratings_query)
            result['ratings'] = [dict(row) for row in ratings.fetchall()]
            return flask.jsonify(result)
        else:
            return abort_json(404, 'no such id')


PAGE_SIZE = 5


@main.route('/leads')
@login_used
def filter_all(uid):
    return filter_leads(uid)


@main.route('/leads/flagged')
@login_required
def filter_flagged(uid):
    return filter_leads(uid, flagged=True)


def filter_leads(uid, flagged=False):
    """Queries should have the form /api/leads?filter=...&from=...&to=...&source=...&page=n where:

    - filter defines the keyword(s) to use to search
    - from / to are start / end dates to search within
    - federal / regional / local define source filters which are matched on equality. "exclude" is a special value that indicates they should not be included.
    - page is a number from 1 to ...
    """
    filter_ = request.args.get('filter', None)
    from_ = request.args.get('from', None)
    to = request.args.get('to', None)
    page = request.args.get('page', 1, int)

    query = build_filtered_lead_selection(
        filter_, from_, to, request.args, page, uid, flagged_only=flagged)

    with engine().begin() as con:

        result = con.execute(query)

        results = list(result.fetchall())

        res_map = {res['id']: {'ratings': [], **dict(res.items())}
                   for res in results}

        if len(results) == 0:
            # no need to do more queries. return empty result
            return flask.jsonify({
                'num_pages': 0,
                'num_results': 0,
                'page': 1,
                'leads': []
            })

        # count total results so we know the page count
        count_query = build_filtered_lead_selection(filter_, from_, to, request.args, page=None, uid=uid,
                                                    fields=[text('count(*) as num_results')], flagged_only=flagged)
        result = con.execute(count_query)

        meta = dict(result.fetchone().items())
        print(meta)

        meta['num_pages'] = ceil(meta['num_results'] / PAGE_SIZE)
        meta['page'] = page
        if 'flagged' in meta:
            del meta['flagged']

        ratings_query = select([crowd_ratings]).where(
            crowd_ratings.c.lead_id.in_(tuple(res_map.keys())))
        ratings = con.execute(ratings_query)

        for rating in ratings:
            lead = res_map[rating['lead_id']]
            lead['ratings'].append(dict(rating.items()))

        result = {
            'leads': list(res_map.values()),
            **meta
        }
        return flask.jsonify(result)


app.register_blueprint(main)
