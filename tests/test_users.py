from tests.conftest import get_token, auth_headers


def test_get_current_user(client):
    token = get_token(
        client,
        email="me@example.com",
        username="meuser",
        password="12345678",
    )

    response = client.get(
        "/users/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "meuser"
    assert "id" in data


def test_get_current_user_without_token(client):
    response = client.get("/users/me")
    assert response.status_code in (401, 403)


def test_get_current_user_with_invalid_token(client):
    response = client.get(
        "/users/me",
        headers=auth_headers("invalid.token.value"),
    )

    assert response.status_code in (401, 403)


def test_get_current_user_returns_only_current_user_data(client):
    token1 = get_token(
        client,
        email="first@example.com",
        username="firstuser",
        password="12345678",
    )
    get_token(
        client,
        email="second@example.com",
        username="seconduser",
        password="12345678",
    )

    response = client.get(
        "/users/me",
        headers=auth_headers(token1),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "first@example.com"
    assert data["username"] == "firstuser"
    assert data["email"] != "second@example.com"
    assert data["username"] != "seconduser"


