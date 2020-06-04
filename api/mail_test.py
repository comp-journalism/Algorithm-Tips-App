from api.mail import send_confirmation, MailSingleton, render_alert, render_confirmation_email
from api.models import pending_confirmations
from sqlalchemy.sql import select
import pytest
from datetime import datetime
from freezegun import freeze_time


@pytest.fixture
def mock_mail_singleton(mocker):
    return mocker.patch.object(MailSingleton, 'get_mailer')


def test_confirmation_no_reconfirm(sqlite_connection, confirmed_email, alert_app, mock_mail_singleton):
    """Test that send_confirmation won't send a confirmation to a confirmed email."""

    with sqlite_connection.connect() as conn, alert_app.app_context():
        query = select([pending_confirmations])
        res = conn.execute(query).fetchall()

        assert len(res) == 0

        send_confirmation(1, 'test@test.net', conn)

        query = select([pending_confirmations])
        res = conn.execute(query).fetchall()

        assert len(res) == 0

        mock_mail_singleton.assert_not_called()


@freeze_time('2020-06-04')
def test_alert_render(alert_app, snapshot):
    ALERT = {'send_id': 1, 'user_id': 1, 'federal_source': 'Federal Agency - Executive', 'regional_source': 'exclude', 'local_source': None, 'frequency': 0, 'recipient': 'test@test.net', 'filter': '', 'alert_id': 1, 'send_date': datetime(2020, 6, 3, 14, 46, 27, 817514)}
    LEADS = [{'name': "FEMA's Climate Impact Model", 'link': 'http://db.algorithmtips.org/lead/6933'}]
    with alert_app.app_context():
        (render_html, render_text) = render_alert(ALERT, LEADS)
    snapshot.assert_match(render_html)
    snapshot.assert_match(render_text)


@freeze_time('2020-06-04')
def test_render_confirmation(alert_app, snapshot):
    with alert_app.app_context():
        (render_html, render_text) = render_confirmation_email(1001)
    snapshot.assert_match(render_html)
    snapshot.assert_match(render_text)
