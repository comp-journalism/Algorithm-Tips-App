import cProfile
from math import ceil
import flask
from flask import request, send_from_directory, send_file
from flask_cors import CORS

import pymysql
import pymysql.cursors
from pymysqlpool.pool import Pool

import configparser
import json


# def create_app():
app = flask.Flask(__name__)
CORS(app)


global_pool = None


@app.before_first_request
def init_pool():
    global global_pool
    if global_pool is not None:
        return

    # Load KEYS.config file
    config = configparser.ConfigParser()
    config.read("keys.conf")

    # AWS Database information
    aws_username = config.get("AWSDatabaseConfig", "username")
    aws_password = config.get("AWSDatabaseConfig", "password")
    aws_host = config.get("AWSDatabaseConfig", "host")
    aws_database = config.get("AWSDatabaseConfig", "database")

    global_pool = Pool(user=aws_username, password=aws_password,
                       host=aws_host, port=3306, db=aws_database, charset='utf8mb4', autocommit=True)


def make_connection():
    return global_pool.get_conn()


def release_connection(conn):
    return global_pool.release(conn)


def build_leads_query(where, extra=''):
    return f"""
        select
            al.lead_id as id, al.name, al.description, al.topic, 
            l.discovered_dt, l.query_term, l.link, l.domain, l.jurisdiction,
            l.source, l.people, l.organizations, l.document_ext, l.document_relevance
        from annotated_leads al
        join leads l on al.lead_id = l.id
        where {where or '1 = 1'} and al.is_published = 1
        {extra};
    """


@app.route('/lead/<lead_id>')
def get_lead(lead_id):
    db = make_connection()
    cur = db.cursor(pymysql.cursors.DictCursor)

    count = cur.execute(build_leads_query("l.id = %s"), lead_id)

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
        return flask.abort(404)


PAGE_SIZE = 5


@app.route('/leads')
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

    limit = f'order by l.id limit %(page_start)s,%(page_size)s'

    db = make_connection()
    cur = db.cursor(pymysql.cursors.DictCursor)

    qstring = ' and '.join(where)

    query = build_leads_query(qstring, limit)

    qparams = {
        'filter': filter_,
        'from': from_,
        'to': to,
        'source': source,
        'page_start': (page - 1) * PAGE_SIZE,
        'page_size': PAGE_SIZE
    }

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

    cur.execute('select * from crowd_ratings where lead_id in %s',
                (tuple(res['id'] for res in results),))
    ratings = list(cur.fetchall())

    res_map = {res['id']: {'ratings': [], **res} for res in results}

    for rating in ratings:
        lead = res_map[rating['lead_id']]
        lead['ratings'].append(rating)

    cur.close()
    release_connection(db)

    result = {
        'leads': list(res_map.values()),
        **meta
    }
    return flask.jsonify(result)
# return app
