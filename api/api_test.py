from api.models import crowd_ratings


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
