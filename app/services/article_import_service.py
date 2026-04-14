import json

import httpx
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import Article, User
from app.services.notification_service import notify_subscribers_about_articles
from app.utils.url_validation import validate_external_url


def _validate_articles_payload(
    articles_data: object, source_name: str
) -> list[dict]:
    if not isinstance(articles_data, list):
        raise HTTPException(
            status_code=400,
            detail=f"{source_name} must contain a list of articles",
        )

    validated_items: list[dict] = []

    for item in articles_data:
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=400,
                detail="Each article must be an object",
            )

        title = item.get("title")
        content = item.get("content")

        if not title or not content:
            raise HTTPException(
                status_code=400,
                detail="Each article must contain title and content",
            )

        validated_items.append(
            {
                "title": title,
                "content": content,
            }
        )

    return validated_items


def _create_articles(
    db: Session,
    current_user: User,
    articles_data: list[dict],
) -> list[Article]:
    imported_articles: list[Article] = []

    for item in articles_data:
        article = Article(
            title=item["title"],
            content=item["content"],
            author_id=current_user.id,
        )
        db.add(article)
        imported_articles.append(article)

    db.commit()

    for article in imported_articles:
        db.refresh(article)

    return imported_articles


async def import_articles_from_file_service(
    db: Session,
    current_user: User,
    file: UploadFile,
) -> dict[str, int]:
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400, detail="Only JSON files are allowed"
        )

    try:
        content = await file.read()
        articles_data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    validated_articles = _validate_articles_payload(articles_data, "JSON")
    imported_articles = _create_articles(db, current_user, validated_articles)
    notify_subscribers_about_articles(db, current_user, imported_articles)

    return {"imported_count": len(imported_articles)}


def import_articles_from_url_service(
    db: Session,
    current_user: User,
    url: str,
) -> dict[str, int]:
    validate_external_url(url)

    try:
        response = httpx.get(
            url,
            timeout=10.0,
            follow_redirects=False,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=400, detail="Failed to fetch articles from URL"
        )

    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        raise HTTPException(
            status_code=400, detail="URL must return JSON data"
        )

    if len(response.content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Response too large")

    try:
        articles_data = response.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON response")

    validated_articles = _validate_articles_payload(
        articles_data, "External data"
    )
    imported_articles = _create_articles(db, current_user, validated_articles)
    notify_subscribers_about_articles(db, current_user, imported_articles)

    return {"imported_count": len(imported_articles)}
