import cProfile
from math import ceil
import flask
from flask import request, send_from_directory, send_file
from flask_cors import CORS
import configparser
from sqlalchemy.sql import select, and_, text

from api.db import init_pool, engine
from api.mail import init_mail
from api.models import users, annotated_leads, leads, crowd_ratings, flags
from api.auth import signup, parse_token, auth, login_used, login_required
from api.flags import flags as flags_bp
from api.alerts import alerts, init_alerts

import json
from os import environ

SOURCES = None


def load_sources():
    global SOURCES
    with open('data/sources.json') as f:
        SOURCES = json.load(f)


app = flask.Flask(__name__)
cfg = configparser.ConfigParser()
cfg.read('keys.conf')
app.secret_key = cfg.get('flask', 'session-key')
CORS(app, supports_credentials='DEBUG' in environ)

init_mail()

app.register_blueprint(flags_bp)
app.register_blueprint(auth)
app.register_blueprint(alerts)
app.before_first_request(init_pool)
app.before_first_request(load_sources)
app.before_first_request(init_alerts)

LEAD_FIELDS = [
    leads.c.id,
    annotated_leads.c.name,
    annotated_leads.c.description,
    annotated_leads.c.topic,
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

    return query.where(and_(annotated_leads.c.is_published == True, *where))


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
        where.append(leads.c.discovered_dt >= from_)
    if to is not None and to != '':
        where.append(leads.c.discovered_dt <= to)

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

    if len(source_values) > 0:
        where.append(leads.c.jurisdiction.in_(source_values))

    query = build_lead_selection(
        uid=uid, fields=fields, where=where, flagged_only=flagged_only)

    if page is not None:
        query = query.order_by(leads.c.id)\
            .limit(PAGE_SIZE).offset(PAGE_SIZE * (page - 1))

    return query


@app.route('/lead/<lead_id>')
@login_used
def get_lead(uid, lead_id):
    with engine().begin() as con:
        query = build_lead_selection(uid, where=[leads.c.id == lead_id])

        resultset = con.execute(query)
        if resultset.rowcount >= 1:
            result = dict(resultset.fetchone().items())

            # now we load comments for it
            ratings_query = select([crowd_ratings])\
                .where(crowd_ratings.c.id == lead_id)
            ratings = con.execute(ratings_query)
            result['ratings'] = ratings.fetchall()
            return flask.jsonify(result)
        else:
            return flask.abort(404)


PAGE_SIZE = 5


@app.route('/leads')
@login_used
def filter_all(uid):
    return filter_leads(uid)


@app.route('/leads/flagged')
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
# return app
