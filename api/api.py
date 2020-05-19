import flask
from flask import request
from flask_cors import CORS

import pymysql
import pymysql.cursors

import configparser
import json


# Load KEYS.config file
config = configparser.ConfigParser()
config.read("keys.conf")

# AWS Database information
aws_username = config.get("AWSDatabaseConfig", "username")
aws_password = config.get("AWSDatabaseConfig", "password")
aws_host = config.get("AWSDatabaseConfig", "host")
aws_database = config.get("AWSDatabaseConfig", "database")

# def create_app():
app = flask.Flask(__name__)
CORS(app)


def make_connection():
    # TODO: the app should instead instantiate a connection pool on start
    return pymysql.connect(user=aws_username,  # Username of AWS database
                           passwd=aws_password,  # AWS Database password
                           host=aws_host,  # AWS Instance
                           port=3306,
                           database=aws_database,
                           charset='utf8mb4')


@app.route('/')
def hello_world():
    return flask.jsonify({"test": "Hello world"})


@app.route('/leads')
def get_leads():
    db = make_connection()
    cur = db.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT al.lead_id, al.name, al.description, al.topic, l.discovered_dt, l.query_term, l.link, l.domain, l.jurisdiction, l.source, l.people, l.organizations, l.document_ext, l.document_relevance FROM annotated_leads al, leads l WHERE al.lead_id = l.id AND al.is_published = 1;")
    results = list(cur.fetchall())

    # TODO limit the number of people and organizations returned by filtering out entites occuring less than N times.

    cur.close()
    db.close()
    return flask.jsonify(results)


@app.route('/lead_ratings/<lead_id>')
def get_ratings(lead_id):
    db = make_connection()
    cur = db.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT * FROM crowd_ratings WHERE lead_id = %s;", (lead_id))
    results = list(cur.fetchall())

    cur.close()
    db.close()
    return flask.jsonify(results)


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


@app.route('/api/lead/<lead_id>')
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
        db.close()
        result['ratings'] = ratings
        return flask.jsonify(result)
    else:
        return flask.abort(404)


@app.route('/api/leads')
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
        where.append("source = %(source)s")

    limit = f'order by l.id limit %(page_start)s,%(page_size)s'

    db = make_connection()
    cur = db.cursor(pymysql.cursors.DictCursor)

    query = build_leads_query(' and '.join(where), limit)

    print(query)

    cur.execute(query, {
        'filter': filter_,
        'from': from_,
        'to': to,
        'source': source,
        'page_start': (page - 1) * 10,
        'page_size': 10
    })

    results = list(cur.fetchall())

    if len(results) == 0:
        # no need to do more queries. return empty result
        cur.close()
        db.close()
        return flask.jsonify(results)

    cur.execute('select * from crowd_ratings where lead_id in %s',
                (tuple(res['id'] for res in results),))
    ratings = list(cur.fetchall())

    res_map = {res['id']: {'ratings': [], **res} for res in results}

    for rating in ratings:
        lead = res_map[rating['lead_id']]
        lead['ratings'].append(rating)

    cur.close()
    db.close()
    return flask.jsonify(list(res_map.values()))


# return app
