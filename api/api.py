import cProfile
from math import ceil
import flask
from flask import request, send_from_directory, send_file
from flask_cors import CORS
import configparser

import pymysql.cursors
from api.db import init_pool, make_connection, release_connection
from api.auth import signup, parse_token, auth, login_used, login_required
from api.flags import flags
from api.alerts import alerts

import json
from os import environ

# def create_app():
app = flask.Flask(__name__)
cfg = configparser.ConfigParser()
cfg.read('keys.conf')
app.secret_key = cfg.get('flask', 'session-key')
CORS(app, supports_credentials='DEBUG' in environ)

app.register_blueprint(flags)
app.register_blueprint(auth)
app.register_blueprint(alerts)
app.before_first_request(init_pool)

LEAD_FIELDS = """
al.lead_id as id, al.name, al.description, al.topic, 
l.discovered_dt, l.query_term, l.link, l.domain, l.jurisdiction,
l.source, l.people, l.organizations, l.document_ext, l.document_relevance
"""


def build_lead_selection(uid=None, fields=LEAD_FIELDS, where=[], is_published=True, flagged_only=False, paged=False):
    if uid is not None:
        fields += ', not isnull(uflags.id) as flagged'
        if flagged_only:
            join_type = "inner"
        else:
            join_type = "left"
        flag_join = f"""{join_type} join (
                select flags.id, lead_id 
                from flags
                where flags.user_id = %(uid)s
            ) uflags on uflags.lead_id = l.id"""
    else:
        flag_join = ""

    if paged:
        limit = "limit %(page_start)s, %(page_size)s"
    else:
        limit = ""

    PUB_WHERE = 'al.is_published = 1'
    if is_published:
        if isinstance(where, list):
            where = ' and '.join(where + [PUB_WHERE])
        elif isinstance(where, str):
            where = where + ' and ' + PUB_WHERE

    template = f"""
        select {fields}
        from annotated_leads al
        join leads l on l.id = al.lead_id
        {flag_join}
        where {where}
        order by l.id asc
        {limit};"""

    return template


def load_ratings(cur, ids):
    cur.execute('select * from crowd_ratings where lead_id in %s',
                (tuple(ids),))
    ratings = list(cur.fetchall())
    return ratings


@app.route('/lead/<lead_id>')
@login_used
def get_lead(uid, lead_id):
    try:
        db = make_connection()
        with db.cursor(pymysql.cursors.DictCursor) as cur:
            query = build_lead_selection(uid, where='lead_id = %(lead_id)s')

            count = cur.execute(query, {
                'lead_id': lead_id,
                'uid': uid,
            })

            if count >= 1:
                result = cur.fetchone()

                # now we load comments for it
                ratings = load_ratings(cur, [lead_id])
                cur.close()
                result['ratings'] = ratings
                return flask.jsonify(result)
            else:
                return flask.abort(404)
    finally:
        release_connection(db)


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
    - source is a source filter (matched on equality)
    - page is a number from 1 to ...
    """
    filter_ = request.args.get('filter', None)
    from_ = request.args.get('from', None)
    to = request.args.get('to', None)
    source = request.args.get('source', None)
    page = request.args.get('page', 1, int)

    where = []

    if filter_ is not None:
        where.append(
            "match(al.name, al.description, al.topic) against (%(filter)s in natural language mode)")
    if from_ is not None:
        where.append("discovered_dt >= %(from)s")
    if to is not None:
        where.append("discovered_dt <= %(to)s")
    if source is not None:
        where.append("jurisdiction = %(source)s")

    query = build_lead_selection(
        uid, where=where, paged=True, flagged_only=flagged)

    try:
        db = make_connection()
        with db.cursor(pymysql.cursors.DictCursor) as cur:
            qparams = {
                'filter': filter_,
                'from': from_,
                'to': to,
                'source': source,
                'page_start': (page - 1) * PAGE_SIZE,
                'page_size': PAGE_SIZE,
                'uid': uid
            }

            print(cur.mogrify(query, qparams))
            cur.execute(query, qparams)

            results = list(cur.fetchall())

            if len(results) == 0:
                # no need to do more queries. return empty result
                return flask.jsonify({
                    'num_pages': 0,
                    'num_results': 0,
                    'page': 1,
                    'leads': []
                })

            # count total results so we know the page count
            count_query = build_lead_selection(uid=uid,
                                               fields='count(*) as num_results', where=where, flagged_only=flagged)
            cur.execute(count_query, qparams)

            meta = cur.fetchone()
            print(meta)

            meta['num_pages'] = ceil(meta['num_results'] / PAGE_SIZE)
            meta['page'] = page

            ratings = load_ratings(cur, (res['id'] for res in results))

            res_map = {res['id']: {'ratings': [], **res} for res in results}

            for rating in ratings:
                lead = res_map[rating['lead_id']]
                lead['ratings'].append(rating)

            result = {
                'leads': list(res_map.values()),
                **meta
            }
            return flask.jsonify(result)
    finally:
        release_connection(db)
# return app
