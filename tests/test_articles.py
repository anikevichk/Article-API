def get_token(client):
    client.post(
        "/auth/register",
        json={
            "email": "author@example.com",
            "username": "author",
            "password": "12345678"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "author",
            "password": "12345678"
        }
    )
    return response.json()["access_token"]


def test_create_article(client):
    token = get_token(client)

    response = client.post(
        "/articles",
        json={
            "title": "Test article",
            "content": "Some content"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in (200, 201)
    data = response.json()
    assert data["title"] == "Test article"


def test_get_articles_list(client):
    token = get_token(client)

    client.post(
        "/articles",
        json={
            "title": "Test article",
            "content": "Some content"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.get("/articles")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_create_article_without_token(client):
    response = client.post(
        "/articles",
        json={
            "title": "Test article",
            "content": "Some content"
        }
    )

    assert response.status_code in (401, 403)