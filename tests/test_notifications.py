from tests.conftest import get_token


def test_get_notifications_empty(client):
    token = get_token(
        client,
        email="user@example.com",
        username="user",
        password="12345678",
    )

    response = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_notifications_without_token(client):
    response = client.get("/notifications")
    assert response.status_code in (401, 403)