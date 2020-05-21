import configparser
import pymysql
from pymysqlpool.pool import Pool

global_pool = None


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
