import flask
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


@app.route('/api/lead/<lead_id>')
def get_lead(lead_id):
    db = make_connection()
    cur = db.cursor(pymysql.cursors.DictCursor)

    count = cur.execute("""
        select
            al.lead_id as id, al.name, al.description, al.topic, 
            l.discovered_dt, l.query_term, l.link, l.domain, l.jurisdiction,
            l.source, l.people, l.organizations, l.document_ext, l.document_relevance
        from annotated_leads al
        join leads l on al.lead_id = l.id
        where l.id = %s and al.is_published = 1;
    """, lead_id)

    if count >= 1:
        result = cur.fetchone()
        cur.close()
        db.close()
        return flask.jsonify(result)
    else:
        return flask.abort(404)


@app.route('/lead_ratings/<lead_id>')
def get_ratings(lead_id):
    db = make_connection()
    cur = db.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT * FROM crowd_ratings WHERE lead_id = %s;", (lead_id))
    results = list(cur.fetchall())

    cur.close()
    db.close()
    return flask.jsonify(results)

# return app
