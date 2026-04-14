from tests.conftest import get_token, register_user


def test_subscribe_to_author(client):
    register_user(client, "author@example.com", "author", "12345678")
    token = get_token(client, "reader@example.com", "reader", "12345678")

    response = client.post(
        "/users/author/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in (200, 201)
    data = response.json()
    assert data["subscriber_id"] != data["author_id"]


def test_subscribe_without_token(client):
    register_user(client, "author@example.com", "author", "12345678")

    response = client.post("/users/author/subscribe")
    assert response.status_code in (401, 403)


def test_subscribe_to_nonexistent_author(client):
    token = get_token(client, "reader@example.com", "reader", "12345678")

    response = client.post(
        "/users/no_such_user/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_subscribe_to_yourself(client):
    token = get_token(client, "author@example.com", "author", "12345678")

    response = client.post(
        "/users/author/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400


def test_subscribe_twice(client):
    register_user(client, "author@example.com", "author", "12345678")
    token = get_token(client, "reader@example.com", "reader", "12345678")

    first_response = client.post(
        "/users/author/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first_response.status_code in (200, 201)

    second_response = client.post(
        "/users/author/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert second_response.status_code == 409


def test_unsubscribe_success(client):
    register_user(client, "author@example.com", "author", "12345678")
    token = get_token(client, "reader@example.com", "reader", "12345678")

    client.post(
        "/users/author/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.delete(
        "/users/author/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unsubscribed successfully"


def test_unsubscribe_not_found(client):
    register_user(client, "author@example.com", "author", "12345678")
    token = get_token(client, "reader@example.com", "reader", "12345678")

    response = client.delete(
        "/users/author/subscribe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404