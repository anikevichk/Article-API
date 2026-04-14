from tests.conftest import get_token


def test_get_current_user(client):
    token = get_token(
        client,
        email="me@example.com",
        username="meuser",
        password="12345678",
    )

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "meuser"


def test_get_current_user_without_token(client):
    response = client.get("/users/me")
    assert response.status_code in (401, 403)