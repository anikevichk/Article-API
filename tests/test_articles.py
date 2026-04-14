from tests.conftest import get_token, auth_headers


def test_create_article(client):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    response = client.post(
        "/articles",
        json={
            "title": "Test article",
            "content": "Some content",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in (200, 201)
    data = response.json()
    assert data["title"] == "Test article"
    assert data["content"] == "Some content"
    assert "id" in data


def test_get_articles_list_empty(client):
    response = client.get("/articles")

    assert response.status_code == 200
    assert response.json() == []


def test_get_articles_list_after_create(client):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    client.post(
        "/articles",
        json={
            "title": "Test article",
            "content": "Some content",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get("/articles")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Test article"


def test_create_article_without_token(client):
    response = client.post(
        "/articles",
        json={
            "title": "Test article",
            "content": "Some content",
        },
    )

    assert response.status_code in (401, 403)


def test_create_article_invalid_body(client):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    response = client.post(
        "/articles",
        json={
            "title": "Only title",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_delete_article_with_notifications(client):
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

    client.post(
        "/users/author/subscribe",
        headers={"Authorization": f"Bearer {subscriber_token}"},
    )

    create_response = client.post(
        "/articles",
        json={"title": "Test", "content": "Text"},
        headers={"Authorization": f"Bearer {author_token}"},
    )

    article_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/articles/{article_id}",
        headers={"Authorization": f"Bearer {author_token}"},
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Article deleted"


def test_get_article_by_id_success(client):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    create_response = client.post(
        "/articles",
        json={"title": "Test article", "content": "Some content"},
        headers={"Authorization": f"Bearer {token}"},
    )
    article_id = create_response.json()["id"]

    response = client.get(f"/articles/{article_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == "Test article"
    assert data["content"] == "Some content"


def test_get_article_by_id_not_found(client):
    response = client.get("/articles/9999")

    assert response.status_code == 404


def test_update_article_success(client):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    create_response = client.post(
        "/articles",
        json={"title": "Old title", "content": "Old content"},
        headers={"Authorization": f"Bearer {token}"},
    )
    article_id = create_response.json()["id"]

    response = client.put(
        f"/articles/{article_id}",
        json={"title": "New title", "content": "New content"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["content"] == "New content"


def test_update_article_forbidden(client):
    author_token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )
    other_token = get_token(
        client,
        email="other@example.com",
        username="other",
        password="12345678",
    )

    create_response = client.post(
        "/articles",
        json={"title": "Test", "content": "Text"},
        headers={"Authorization": f"Bearer {author_token}"},
    )
    article_id = create_response.json()["id"]

    response = client.put(
        f"/articles/{article_id}",
        json={"title": "Hack", "content": "Hack"},
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 403


def test_update_article_without_token(client):
    response = client.put(
        "/articles/1",
        json={"title": "New", "content": "New"},
    )

    assert response.status_code in (401, 403)


def test_delete_article_removes_article(client):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    create_response = client.post(
        "/articles",
        json={"title": "Test", "content": "Text"},
        headers={"Authorization": f"Bearer {token}"},
    )
    article_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/articles/{article_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 200

    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 404


def test_delete_article_forbidden(client):
    author_token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )
    other_token = get_token(
        client,
        email="other@example.com",
        username="other",
        password="12345678",
    )

    create_response = client.post(
        "/articles",
        json={"title": "Test", "content": "Text"},
        headers={"Authorization": f"Bearer {author_token}"},
    )
    article_id = create_response.json()["id"]

    response = client.delete(
        f"/articles/{article_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 403


def test_delete_article_without_token(client):
    response = client.delete("/articles/1")

    assert response.status_code in (401, 403)


def test_delete_article_not_found(client):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    response = client.delete(
        "/articles/9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_get_my_articles_only_mine(client):
    my_token = get_token(
        client,
        email="me@example.com",
        username="meuser",
        password="12345678",
    )
    other_token = get_token(
        client,
        email="other@example.com",
        username="other",
        password="12345678",
    )

    client.post(
        "/articles",
        json={"title": "Mine", "content": "My text"},
        headers=auth_headers(my_token),
    )
    client.post(
        "/articles",
        json={"title": "Other", "content": "Other text"},
        headers=auth_headers(other_token),
    )

    response = client.get(
        "/articles/my",
        headers=auth_headers(my_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Mine"
    assert data[0]["content"] == "My text"


def test_get_subscribed_articles_only_from_subscribed_authors(client):
    author1_token = get_token(
        client,
        email="author1@example.com",
        username="author1",
        password="12345678",
    )
    author2_token = get_token(
        client,
        email="author2@example.com",
        username="author2",
        password="12345678",
    )
    reader_token = get_token(
        client,
        email="reader@example.com",
        username="reader",
        password="12345678",
    )

    client.post(
        "/users/author1/subscribe",
        headers=auth_headers(reader_token),
    )

    client.post(
        "/articles",
        json={"title": "From author1", "content": "Text1"},
        headers=auth_headers(author1_token),
    )
    client.post(
        "/articles",
        json={"title": "From author2", "content": "Text2"},
        headers=auth_headers(author2_token),
    )

    response = client.get(
        "/articles/subscribed",
        headers=auth_headers(reader_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "From author1"
    assert data[0]["content"] == "Text1"