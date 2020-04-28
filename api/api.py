import flask

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

def create_app():
    app = flask.Flask(__name__)

    def make_connection():
        return pymysql.connect(user= aws_username,  # Username of AWS database
                        passwd= aws_password,  # AWS Database password
                        host= aws_host,  # AWS Instance
                        port=3306,
                        database= aws_database,
                        charset='utf8mb4')


    @app.route('/')
    def hello_world():
        return flask.jsonify({"test": "Hello world"})
    
    @app.route('/scrapes')
    def get_scrape():
        db = make_connection()
        cur = db.cursor(pymysql.cursors.DictCursor)

        cur.execute("SELECT * from scrapes")
        results = list(cur.fetchall())

        cur.close()
        db.close()
        return flask.jsonify(results)

    @app.route('/leads')
    def get_leads():
        db = make_connection()
        cur = db.cursor(pymysql.cursors.DictCursor)

        cur.execute("SELECT name, description, topic, jurisdiction, agency, lead_id, scrape_id, discovered_dt, query_term, link, snippet, government_level, document_ext, document_relevance FROM annotated_leads al, leads l WHERE al.lead_id = l.id AND al.is_algorithm = 1 AND l.is_duplicate = 0")
        results = list(cur.fetchall())

        cur.close()
        db.close()
        return flask.jsonify(results)



    return app