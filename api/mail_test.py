from api.mail import send_confirmation, MailSingleton
from api.models import pending_confirmations
from sqlalchemy.sql import select
import pytest


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
