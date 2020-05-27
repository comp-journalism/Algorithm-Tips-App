import configparser
import pymysql
from pymysqlpool.pool import Pool
from pymysql.err import OperationalError, InterfaceError
from contextlib import contextmanager

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
                       host=aws_host, port=3306, db=aws_database, charset='utf8mb4', autocommit=True, ping_check=True)


def make_connection():
    return global_pool.get_conn()


def release_connection(conn):
    return global_pool.release(conn)


def kill_connection(conn):
    with global_pool.cond:
        global_pool.current_size -= 1
        global_pool.inuse_list.remove(conn)
        conn.close()
        global_pool.cond.notify_all()


@contextmanager
def connect():
    con = make_connection()
    try:
        yield con
    except (OperationalError, InterfaceError) as err:
        # these errors indicate a dead or broken connection
        print(err)
        print('Killing connection')
        kill_connection(con)
    finally:
        if con.open:
            release_connection(con)
