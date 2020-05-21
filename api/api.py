import cProfile
from math import ceil
import flask
from flask import request, send_from_directory, send_file
from flask_cors import CORS

import pymysql.cursors
from api.db import init_pool, make_connection, release_connection
from api.auth import signup, parse_token
from api.flags import flags

import json


# def create_app():
app = flask.Flask(__name__)
CORS(app)

app.register_blueprint(flags)
app.before_first_request(init_pool)

LEAD_FIELDS = """
al.lead_id as id, al.name, al.description, al.topic, 
l.discovered_dt, l.query_term, l.link, l.domain, l.jurisdiction,
l.source, l.people, l.organizations, l.document_ext, l.document_relevance
"""


def load_ratings(cur, ids):
    cur.execute('select * from crowd_ratings where lead_id in %s',
                (tuple(ids),))
    ratings = list(cur.fetchall())
    return ratings


@app.route('/lead/<lead_id>')
def get_lead(lead_id):
    db = make_connection()
    cur = db.cursor(pymysql.cursors.DictCursor)

    query = f"""
        select {LEAD_FIELDS}
        from annotated leads al
        join leads l on al.lead_id = l.id
        where l.id = %s and al.is_published = 1;
    """

    count = cur.execute(query, lead_id)

    if count >= 1:
        result = cur.fetchone()

        # now we load comments for it
        cur.execute("select * from crowd_ratings where lead_id = %s;", lead_id)
        ratings = list(cur.fetchall())
        cur.close()
        release_connection(db)
        result['ratings'] = ratings
        return flask.jsonify(result)
    else:
        release_connection(db)
        return flask.abort(404)


PAGE_SIZE = 5


# TODO: this monster needs some pruning/splitting
@app.route('/leads', methods=('GET', 'POST'))
def filter_leads():
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
    flagged = request.args.get('flagged', False, bool)

    where = []
    joins = []

    if filter_ is not None:
        where.append(
            "match(al.name, al.description, al.topic) against (%(filter)s in natural language mode)")
    if from_ is not None:
        where.append("discovered_dt >= %(from)s")
    if to is not None:
        where.append("discovered_dt <= %(to)s")
    if source is not None:
        where.append("jurisdiction = %(source)s")

    uid = None
    flag_field = ""
    if request.method == 'POST':
        token = parse_token()
        if token is None:
            # the POST api requires a JSON body
            return flask.abort(400)

        uid = signup(token)

        if uid is None:
            # unable to validate user
            return flask.abort(401)

        flag_field = ", not isnull(uflags.id) as flagged"

        join_type = 'left'
        if flagged:
            # if flagged, then we only get flagged items
            join_type = 'inner'

        joins.append(f"""{join_type} join (
                select flags.id, lead_id 
                from flags
                where flags.user_id = %(uid)s
            ) uflags on uflags.lead_id = l.id""")

    limit = f'order by l.id limit %(page_start)s,%(page_size)s'

    db = make_connection()
    try:
        cur = db.cursor(pymysql.cursors.DictCursor)

        qstring = ' and '.join(where)

        if qstring == '':
            qstring = 'al.is_published = 1'
        else:
            qstring += 'and al.is_published = 1'

        query = f"""
            select {LEAD_FIELDS}{flag_field}
            from annotated_leads al
            join leads l on l.id = al.lead_id
            {' '.join(joins)}
            where {qstring}
            {limit};
        """

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
            cur.close()
            db.close()
            return flask.jsonify({
                'num_pages': 0,
                'num_results': 0,
                'page': 1,
                'leads': []
            })

        # count total results so we know the page count
        cur.execute(
            f"select count(*) as num_results from annotated_leads as al join leads as l on l.id = al.lead_id where {qstring or '1 = 1'} and al.is_published = 1;", qparams)

        meta = cur.fetchone()
        print(meta)

        meta['num_pages'] = ceil(meta['num_results'] / PAGE_SIZE)
        meta['page'] = page

        ratings = load_ratings(cur, (res['id'] for res in results))

        res_map = {res['id']: {'ratings': [], **res} for res in results}

        for rating in ratings:
            lead = res_map[rating['lead_id']]
            lead['ratings'].append(rating)

        cur.close()

        result = {
            'leads': list(res_map.values()),
            **meta
        }
        return flask.jsonify(result)
    finally:
        release_connection(db)
# return app
