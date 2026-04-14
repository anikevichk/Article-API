from tests.conftest import register_user, login_user


def test_register_user_success(client):
    response = register_user(
        client,
        email="test@example.com",
        username="testuser",
        password="12345678",
    )

    assert response.status_code in (200, 201)
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data


def test_register_user_duplicate_email(client):
    register_user(
        client,
        email="same@example.com",
        username="user1",
        password="12345678",
    )

    response = register_user(
        client,
        email="same@example.com",
        username="user2",
        password="12345678",
    )

    assert response.status_code in (400, 409)


def test_login_success(client):
    register_user(
        client,
        email="login@example.com",
        username="loginuser",
        password="12345678",
    )

    response = login_user(client, username="loginuser", password="12345678")

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"


def test_login_wrong_password(client):
    register_user(
        client,
        email="login2@example.com",
        username="loginuser2",
        password="12345678",
    )

    response = login_user(client, username="loginuser2", password="wrongpass")

    assert response.status_code in (400, 401)


def test_register_user_duplicate_username(client):
    register_user(
        client,
        email="user1@example.com",
        username="sameuser",
        password="12345678",
    )

    response = register_user(
        client,
        email="user2@example.com",
        username="sameuser",
        password="12345678",
    )

    assert response.status_code in (400, 409)


def test_register_user_invalid_email(client):
    response = register_user(
        client,
        email="not-an-email",
        username="testuser",
        password="12345678",
    )

    assert response.status_code == 422


def test_register_user_short_password(client):
    response = register_user(
        client,
        email="short@example.com",
        username="shortuser",
        password="123",
    )

    assert response.status_code == 422


def test_register_user_missing_fields(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
        },
    )

    assert response.status_code == 422


def test_login_nonexistent_user(client):
    response = login_user(client, username="ghost", password="12345678")

    assert response.status_code in (400, 401)


def test_login_missing_password(client):
    response = client.post(
        "/auth/login",
        data={"username": "testuser"},
    )

    assert response.status_code == 422


def test_login_missing_username(client):
    response = client.post(
        "/auth/login",
        data={"password": "12345678"},
    )

    assert response.status_code == 422
