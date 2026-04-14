from tests.conftest import get_token, register_user, auth_headers


def setup_author_and_reader(client):
    register_user(client, "author@example.com", "author", "12345678")
    reader_token = get_token(
        client, "reader@example.com", "reader", "12345678"
    )
    return reader_token


def test_subscribe_to_author(client):
    token = setup_author_and_reader(client)

    response = client.post(
        "/users/author/subscribe",
        headers=auth_headers(token),
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
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_subscribe_to_yourself(client):
    token = get_token(client, "author@example.com", "author", "12345678")

    response = client.post(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )

    assert response.status_code == 400


def test_subscribe_twice(client):
    token = setup_author_and_reader(client)

    first_response = client.post(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )
    assert first_response.status_code in (200, 201)

    second_response = client.post(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )

    assert second_response.status_code == 409


def test_unsubscribe_success(client):
    token = setup_author_and_reader(client)

    client.post(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )

    response = client.delete(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unsubscribed successfully"


def test_unsubscribe_not_found(client):
    token = setup_author_and_reader(client)

    response = client.delete(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_unsubscribe_without_token(client):
    register_user(client, "author@example.com", "author", "12345678")

    response = client.delete("/users/author/subscribe")

    assert response.status_code in (401, 403)


def test_unsubscribe_from_nonexistent_author(client):
    token = get_token(client, "reader@example.com", "reader", "12345678")

    response = client.delete(
        "/users/no_such_user/subscribe",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_unsubscribe_after_unsubscribe_returns_not_found(client):
    token = setup_author_and_reader(client)

    client.post(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )

    first_response = client.delete(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )
    assert first_response.status_code == 200

    second_response = client.delete(
        "/users/author/subscribe",
        headers=auth_headers(token),
    )

    assert second_response.status_code == 404