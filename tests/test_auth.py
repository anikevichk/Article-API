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