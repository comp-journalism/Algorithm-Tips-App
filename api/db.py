import configparser
from sqlalchemy import create_engine


class PoolSingleton:
    __engine = None

    @classmethod
    def init(cls):
        # Load KEYS.config file
        config = configparser.ConfigParser()
        config.read("keys.conf")

        # AWS Database information
        aws_username = config.get("AWSDatabaseConfig", "username")
        aws_password = config.get("AWSDatabaseConfig", "password")
        aws_host = config.get("AWSDatabaseConfig", "host")
        aws_database = config.get("AWSDatabaseConfig", "database")

        cls.__engine = create_engine(
            f'mysql+pymysql://{aws_username}:{aws_password}@{aws_host}/{aws_database}', echo=True)

    @classmethod
    def get_engine(cls):
        assert cls.__engine is not None
        return cls.__engine


def init_pool():
    return PoolSingleton.init()


def engine():
    return PoolSingleton.get_engine()
