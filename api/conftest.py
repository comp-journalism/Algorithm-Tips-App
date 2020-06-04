import pytest
import tempfile
import shutil
from flask import Flask
from sqlalchemy import create_engine
from api import alerts
from api.models import confirmed_emails


@pytest.fixture
def sqlite_connection(mocker):
    with tempfile.NamedTemporaryFile() as tmp:
        shutil.copy('test-db.sqlite', tmp.name)
        engine = create_engine(f"sqlite:///{tmp.name}")
        mocker.patch('api.alerts.engine', lambda: engine)
        yield engine


@pytest.fixture
def alert_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['ALERT_TRIGGER_WHITELIST'] = '127.0.0.1'
    app.secret_key = b'testtesttest'
    app.register_blueprint(alerts.alerts)
    return app


@pytest.fixture
def confirmed_email(sqlite_connection):
    with sqlite_connection.connect() as conn:
        res = conn.execute(confirmed_emails.insert().values(  # pylint: disable=no-value-for-parameter
            user_id=1,
            email='test@test.net'
        ))

        assert res.rowcount == 1
