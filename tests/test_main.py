def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API works"}


def test_db_health(client):
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}