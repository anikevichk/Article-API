import httpx

from tests.conftest import get_token, auth_headers


def test_import_articles_from_file_success(client):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    file_content = b"""
    [
        {"title": "Imported 1", "content": "Content 1"},
        {"title": "Imported 2", "content": "Content 2"}
    ]
    """

    response = client.post(
        "/articles/import-file",
        files={"file": ("articles.json", file_content, "application/json")},
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    articles_response = client.get("/articles")
    assert articles_response.status_code == 200
    articles = articles_response.json()

    titles = [article["title"] for article in articles]
    assert "Imported 1" in titles
    assert "Imported 2" in titles


def test_import_articles_from_url_success(client, monkeypatch):
    token = get_token(
        client,
        email="author@example.com",
        username="author",
        password="12345678",
    )

    class MockResponse:
        headers = {"content-type": "application/json"}
        content = b"""
        [
            {"title": "URL Imported 1", "content": "URL Content 1"},
            {"title": "URL Imported 2", "content": "URL Content 2"}
        ]
        """

        def raise_for_status(self):
            pass

        def json(self):
            return [
                {"title": "URL Imported 1", "content": "URL Content 1"},
                {"title": "URL Imported 2", "content": "URL Content 2"},
            ]

    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: MockResponse())

    response = client.post(
        "/articles/import-from-url",
        json={"url": "https://example.com/articles.json"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    articles_response = client.get("/articles")
    assert articles_response.status_code == 200
    articles = articles_response.json()

    titles = [article["title"] for article in articles]
    assert "URL Imported 1" in titles
    assert "URL Imported 2" in titles