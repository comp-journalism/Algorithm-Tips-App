from api.models import crowd_ratings
import datetime


def test_get_lead_returns_ratings(sqlite_connection, api_app):
    """Test that the `get_lead` endpoint returns ratings as well."""
    with sqlite_connection.connect() as conn, api_app.test_client(True) as client:
        lead_id = 6933
        ratings = conn.execute(crowd_ratings.select()
                               .where(crowd_ratings.c.lead_id == lead_id))
        ratings = [dict(row) for row in ratings]
        assert len(ratings) > 0

        res = client.get(f'/lead/{lead_id}')

        assert res.status_code == 200
        data = res.get_json()

        assert data['id'] == lead_id
        assert data['ratings'] == ratings


def test_filtered_leads_exact_day(sqlite_connection, api_app):
    with api_app.test_client(True) as client:
        date = datetime.date.fromisoformat('2019-06-30')
        res = client.get(f'/leads?from={date.isoformat()}&to={date.isoformat()}')

        assert res.status_code == 200
        data = res.get_json()

        assert len(data['leads']) == 2
        for lead in data['leads']:
            lead_dt = datetime.datetime.strptime(lead['published_dt'], '%a, %d %b %Y %H:%M:%S GMT')
            assert lead_dt.date() == date
