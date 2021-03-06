from datetime import datetime, timedelta

import pytest
from sqlalchemy.sql import select, and_
from freezegun import freeze_time

from api.alerts import CONFIRMATION_NOTE
from api.mail import get_private_alert_token
from api.models import (annotated_leads, confirmed_emails, sent_alert_contents,
                        sent_alerts, alerts as alerts_)


@pytest.fixture
def send_confirmation(mocker):
    return mocker.patch('api.alerts.send_confirmation')


@pytest.fixture
def send_alert(mocker):
    return mocker.patch('api.alerts.send_alert')


def update_published_dt(conn, dt, lead_id):
    return conn.execute(annotated_leads.update().values(  # pylint: disable=no-value-for-parameter
        published_dt=dt
    ).where(annotated_leads.c.lead_id == lead_id))


@pytest.fixture
def trigger_published_dt(sqlite_connection):
    with sqlite_connection.connect() as conn:
        res = update_published_dt(conn, datetime.now(), 6933)
        assert res.rowcount == 1


def test_list_alerts_requires_login(sqlite_connection, alert_app):
    with alert_app.test_client(True) as client:
        res = client.get('/alert/list')
        assert res.status_code == 401
        with client.session_transaction() as sess:
            sess['id'] = 1
        res = client.get('/alert/list')
        assert res.status_code == 200
        assert len(res.get_json()['alerts']) == 0


def test_create_alert_logged_in(sqlite_connection, alert_app, send_confirmation):
    with alert_app.test_client(True) as client:
        with client.session_transaction() as sess:
            sess['id'] = 1

        res = client.post('/alert/create', json={
            'filter': '',
            'recipient': 'test@test.net',
            'sources': {},
            'frequency': 0,
        })

        # success
        assert res.status_code == 200
        assert res.get_json() == {
            'id': 1,
            'status': 'ok',
            'notes': [CONFIRMATION_NOTE]
        }

        # sends confirmation
        (left, _) = send_confirmation.call_args
        (uid, recip, _) = left
        assert uid == 1 and recip == 'test@test.net'


def test_create_alert_invalid_email(sqlite_connection, alert_app, send_confirmation):
    with alert_app.test_client(True) as client:
        with client.session_transaction() as sess:
            sess['id'] = 1

        res = client.post('/alert/create', json={
            'filter': '',
            'recipient': 'bad email',
            'sources': {},
            'frequency': 0
        })

        assert res.status_code == 400
        assert res.get_json()[
            'reason'] == 'Unable to read or validate alert data'


def test_trigger_unconfirmed_email(sqlite_connection, send_alert, alert_app, trigger_published_dt):
    """Test triggering alerts when the email is not confirmed. Should not send email."""
    with alert_app.test_client(True) as client:
        with client.session_transaction() as sess:
            sess['id'] = 1

        res = client.post('/alert/create', json={
            'filter': '',
            'recipient': 'test@test.net',
            'sources': {},
            'frequency': 0
        })

        assert res.status_code == 200

    with alert_app.test_client(False) as client:
        res = client.post('/alert/trigger')
        assert res.status_code == 200

    with sqlite_connection.connect() as conn:
        sent_alert_results = conn.execute(select([sent_alerts]))
        rows = list(dict(row) for row in sent_alert_results)
        assert len(rows) == 0

    send_alert.assert_not_called()


def test_trigger_initial_send(sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt):
    """Test sending the first alert email to a recipient that has never received one."""
    with alert_app.test_client(True) as client:
        with client.session_transaction() as sess:
            sess['id'] = 1

        res = client.post('/alert/create', json={
            'filter': '',
            'recipient': 'test@test.net',
            'sources': {'local': 'exclude', 'regional': 'exclude'},
            'frequency': 0
        })

        assert res.status_code == 200
        alert_id = res.get_json()['id']

    with alert_app.test_client(False) as client:
        res = client.post('/alert/trigger')
        assert res.status_code == 200

    with sqlite_connection.connect() as conn:
        sent_alert_results = conn.execute(select([sent_alerts]))
        rows = list(dict(row) for row in sent_alert_results)
        assert len(rows) == 1
        sent = rows[0]
        assert sent['alert_id'] == alert_id

        contents = conn.execute(
            select([sent_alert_contents.c.send_id, sent_alert_contents.c.lead_id]))
        rows = list(dict(row) for row in contents)
        assert rows == [{'send_id': 1, 'lead_id': 6933}]

    send_alert.assert_called()


def test_trigger_no_contents(sqlite_connection, send_alert, alert_app, confirmed_email):
    """Test sending the alert email when there is no new content. It should not record any new data in the DB."""
    with alert_app.test_client(True) as client:
        with client.session_transaction() as sess:
            sess['id'] = 1

        res = client.post('/alert/create', json={
            'filter': '',
            'recipient': 'test@test.net',
            'sources': {},
            'frequency': 0
        })

        assert res.status_code == 200

    with alert_app.test_client(False) as client:
        res = client.post('/alert/trigger')
        assert res.status_code == 200

    with sqlite_connection.connect() as conn:
        sent_alert_results = conn.execute(select([sent_alerts]))
        rows = list(dict(row) for row in sent_alert_results)
        assert len(rows) == 0

    send_alert.assert_not_called()


def test_trigger_too_recent(sqlite_connection, send_alert, alert_app, trigger_published_dt, confirmed_email):
    """Test sending the alert email when the last trigger was too recent."""
    # do the initial send
    test_trigger_initial_send(
        sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt)

    # trigger again
    with alert_app.test_client(False) as client:
        res = client.post('/alert/trigger')
        assert res.status_code == 200

    with sqlite_connection.connect() as conn:
        sent_alert_results = conn.execute(select([sent_alerts]))
        rows = list(dict(row) for row in sent_alert_results)
        assert len(rows) == 1

    send_alert.assert_called()


class NextWeek:
    def now(self):
        return datetime.now() + timedelta(weeks=1)


def test_trigger_next_email_no_new(sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt, mocker):
    """Test sending the alert email when the last trigger was in the previous period and there are no new items."""
    # send previous email
    test_trigger_initial_send(
        sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt)

    mocker.patch('api.alerts.datetime', NextWeek())

    # trigger again
    with alert_app.test_client(False) as client:
        res = client.post('/alert/trigger')
        assert res.status_code == 200

    # there should not be another alert sent
    with sqlite_connection.connect() as conn:
        sent_alert_results = conn.execute(select([sent_alerts]))
        rows = list(dict(row) for row in sent_alert_results)
        assert len(rows) == 1

    send_alert.assert_called_once()


def test_trigger_next_email_with_new(sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt, mocker):
    """Test sending the alert email when the last trigger was in the previous period and there are new items."""
    # send previous email
    test_trigger_initial_send(
        sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt)

    with sqlite_connection.connect() as conn:
        update_published_dt(conn, datetime.now() + timedelta(days=2), 1420)

    mocker.patch('api.alerts.datetime', NextWeek())

    # trigger again
    with alert_app.test_client(False) as client:
        res = client.post('/alert/trigger')
        assert res.status_code == 200

    # there should be another alert sent
    with sqlite_connection.connect() as conn:
        sent_alert_results = conn.execute(
            select([sent_alerts.c.id, sent_alerts.c.alert_id]))
        rows = list(dict(row) for row in sent_alert_results)
        assert rows == [{'id': 1, 'alert_id': 1},
                        {'id': 2, 'alert_id': 1}]

        contents = conn.execute(
            select([sent_alert_contents.c.send_id, sent_alert_contents.c.lead_id]))
        rows = list(dict(row) for row in contents)
        assert rows == [{'send_id': 1, 'lead_id': 6933},
                        {'send_id': 2, 'lead_id': 1420}]

    assert send_alert.call_count == 2


def test_alert_delete_via_link(sqlite_connection, alert_app, send_alert, confirmed_email, trigger_published_dt):
    """Test that we can successfully delete an alert via the link in an email."""
    test_trigger_initial_send(sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt)

    with alert_app.app_context():
        token = get_private_alert_token(1, 1)

    with sqlite_connection.connect() as conn:
        res = conn.execute(select([alerts_]).where(and_(alerts_.c.id == 1, alerts_.c.user_id == 1)))

        assert len(list(dict(r) for r in res)) == 1

    with alert_app.test_client(False) as client:
        res = client.get(f'/alert/delete?token={token}')
        assert res.status_code == 200

    with sqlite_connection.connect() as conn:
        res = conn.execute(select([alerts_]).where(and_(alerts_.c.id == 1, alerts_.c.user_id == 1)))

        assert len(list(dict(r) for r in res)) == 0


def test_alert_unsubscribe_via_link(sqlite_connection, alert_app, send_alert, confirmed_email, trigger_published_dt):
    """Test that we can successfully delete an alert via the link in an email."""
    test_trigger_initial_send(sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt)

    with alert_app.app_context():
        token = get_private_alert_token(1, 1)

    with sqlite_connection.connect() as conn:
        conn.execute(alerts_.insert().values(
            recipient='test@test.net',
            filter='test',
            frequency=1,
            user_id=1,
        ))
        res = conn.execute(select([alerts_]).where(alerts_.c.recipient == 'test@test.net'))

        assert len(list(dict(r) for r in res)) == 2

    with alert_app.test_client(False) as client:
        res = client.get(f'/alert/unsubscribe?token={token}')
        assert res.status_code == 200

    with sqlite_connection.connect() as conn:
        res = conn.execute(select([alerts_]).where(alerts_.c.recipient == 'test@test.net'))

        assert len(list(dict(r) for r in res)) == 0

        res = conn.execute(select([confirmed_emails]).where(confirmed_emails.c.email == 'test@test.net'))
        assert len(list(dict(r) for r in res)) == 0


@freeze_time('2020-06-04')
def test_alert_db_link(sqlite_connection, alert_app, send_alert, confirmed_email, trigger_published_dt, snapshot):
    """Test that the DB deep link gets added to the table correctly."""
    test_trigger_initial_send(sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt)

    with sqlite_connection.connect() as conn:
        res = conn.execute(select([sent_alerts.c.db_link])).fetchone()

        db_link = res['db_link']
        snapshot.assert_match(db_link)


def test_trigger_frequency_parameter(sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt):
    """Test sending the alert when the frequency parameter is set."""
    with alert_app.test_client(True) as client:
        with client.session_transaction() as sess:
            sess['id'] = 1

        res = client.post('/alert/create', json={
            'filter': '',
            'recipient': 'test@test.net',
            'sources': {},
            'frequency': 0
        })

        assert res.status_code == 200

    with alert_app.test_client(False) as client:
        res = client.post('/alert/trigger?frequency=monthly')
        assert res.status_code == 200

    with sqlite_connection.connect() as conn:
        sent_alert_results = conn.execute(select([sent_alerts]))
        rows = list(dict(row) for row in sent_alert_results)
        assert len(rows) == 0

    send_alert.assert_not_called()


def test_trigger_invalid_frequency(sqlite_connection, send_alert, alert_app, confirmed_email, trigger_published_dt):
    with alert_app.test_client(True) as client:
        with client.session_transaction() as sess:
            sess['id'] = 1

        res = client.post('/alert/create', json={
            'filter': '',
            'recipient': 'test@test.net',
            'sources': {},
            'frequency': 0
        })

        assert res.status_code == 200

    with alert_app.test_client(False) as client:
        res = client.post('/alert/trigger?frequency=invalid')
        assert res.status_code == 400

    with sqlite_connection.connect() as conn:
        sent_alert_results = conn.execute(select([sent_alerts]))
        rows = list(dict(row) for row in sent_alert_results)
        assert len(rows) == 0

    send_alert.assert_not_called()
