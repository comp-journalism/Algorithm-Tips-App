import configparser
from sqlalchemy import create_engine

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

    global_pool = create_engine(
        f'mysql+pymysql://{aws_username}:{aws_password}@{aws_host}/{aws_database}', echo=True)


def engine():
    global global_pool
    return global_pool
