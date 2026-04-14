from tests.conftest import get_token, auth_headers


def create_notification_scenario(client, with_other_user=False):
    author_token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )
    subscriber_token = get_token(
        client,
        email="sub@example.com",
        username="subscriber",
        password="12345678",
    )

    other_token = None
    if with_other_user:
        other_token = get_token(
            client,
            email="other@example.com",
            username="other",
            password="12345678",
        )

    client.post(
        "/users/author/subscribe",
        headers=auth_headers(subscriber_token),
    )

    client.post(
        "/articles",
        json={"title": "New article", "content": "Body"},
        headers=auth_headers(author_token),
    )

    notifications_response = client.get(
        "/notifications",
        headers=auth_headers(subscriber_token),
    )

    notifications = notifications_response.json()
    notification_id = notifications[0]["id"] if notifications else None

    return {
        "author_token": author_token,
        "subscriber_token": subscriber_token,
        "other_token": other_token,
        "notifications": notifications,
        "notification_id": notification_id,
    }


def test_get_notifications_empty(client):
    token = get_token(
        client,
        email="user@example.com",
        username="user",
        password="12345678",
    )

    response = client.get(
        "/notifications",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_notifications_without_token(client):
    response = client.get("/notifications")
    assert response.status_code in (401, 403)


def test_notification_created_after_article_publish(client):
    data = create_notification_scenario(client)

    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["is_read"] is False


def test_notifications_visible_only_to_owner(client):
    data = create_notification_scenario(client, with_other_user=True)

    response = client.get(
        "/notifications",
        headers=auth_headers(data["other_token"]),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_mark_notification_as_read_success(client):
    data = create_notification_scenario(client)

    response = client.patch(
        f"/notifications/{data['notification_id']}/read",
        headers=auth_headers(data["subscriber_token"]),
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_mark_notification_as_read_not_found(client):
    token = get_token(
        client,
        email="user@example.com",
        username="user",
        password="12345678",
    )

    response = client.patch(
        "/notifications/9999/read",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_mark_notification_as_read_forbidden_or_not_found(client):
    data = create_notification_scenario(client, with_other_user=True)

    response = client.patch(
        f"/notifications/{data['notification_id']}/read",
        headers=auth_headers(data["other_token"]),
    )

    assert response.status_code in (403, 404)