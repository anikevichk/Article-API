from tests.conftest import get_token


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