import json
import httpx

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models import Article, User, Subscription, Notification
from app.schemas import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleImportResponse,
    ImportFromUrlRequest,
)
from app.security import get_current_user

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    result = db.execute(
        select(Article).order_by(Article.id.desc())
    )
    return result.scalars().all()


@router.get("/my", response_model=list[ArticleResponse])
def get_my_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    articles = db.execute(
        select(Article)
        .where(Article.author_id == current_user.id)
        .order_by(Article.id.desc())
    ).scalars().all()

    return articles


@router.get("/subscribed", response_model=list[ArticleResponse])
def get_subscribed_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscriptions = db.execute(
        select(Subscription.author_id).where(
            Subscription.subscriber_id == current_user.id
        )
    ).scalars().all()

    if not subscriptions:
        return []

    articles = db.execute(
        select(Article)
        .where(Article.author_id.in_(subscriptions))
        .order_by(Article.id.desc())
    ).scalars().all()

    return articles


@router.post("", response_model=ArticleResponse)
def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    article = Article(
        title=article_data.title,
        content=article_data.content,
        author_id=current_user.id
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    subscriptions = db.execute(
        select(Subscription).where(Subscription.author_id == current_user.id)
    ).scalars().all()

    for subscription in subscriptions:
        notification = Notification(
            user_id=subscription.subscriber_id,
            article_id=article.id,
            message=f"New article published by {current_user.username}: {article.title}",
            is_read=False
        )
        db.add(notification)

    db.commit()
    return article


@router.post("/import-file", response_model=ArticleImportResponse)
async def import_articles_from_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")

    try:
        content = await file.read()
        articles_data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    if not isinstance(articles_data, list):
        raise HTTPException(status_code=400, detail="JSON must contain a list of articles")

    imported_articles = []

    for item in articles_data:
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail="Each article must be an object")

        title = item.get("title")
        content = item.get("content")

        if not title or not content:
            raise HTTPException(
                status_code=400,
                detail="Each article must contain title and content"
            )

        article = Article(
            title=title,
            content=content,
            author_id=current_user.id
        )
        db.add(article)
        imported_articles.append(article)

    db.commit()

    subscriptions = db.execute(
        select(Subscription).where(Subscription.author_id == current_user.id)
    ).scalars().all()

    for article in imported_articles:
        db.refresh(article)

        for subscription in subscriptions:
            notification = Notification(
                user_id=subscription.subscriber_id,
                article_id=article.id,
                message=f"New article published by {current_user.username}: {article.title}",
                is_read=False
            )
            db.add(notification)

    db.commit()

    return {"imported_count": len(imported_articles)}


@router.post("/import-from-url", response_model=ArticleImportResponse)
def import_articles_from_url(
    data: ImportFromUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        response = httpx.get(data.url, timeout=10.0)
        response.raise_for_status()
        articles_data = response.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to fetch articles from URL")

    if not isinstance(articles_data, list):
        raise HTTPException(status_code=400, detail="External data must be a list of articles")

    imported_articles = []

    for item in articles_data:
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail="Each imported article must be an object")

        title = item.get("title")
        content = item.get("content")

        if not title or not content:
            raise HTTPException(
                status_code=400,
                detail="Each imported article must contain title and content"
            )

        article = Article(
            title=title,
            content=content,
            author_id=current_user.id
        )
        db.add(article)
        imported_articles.append(article)

    db.commit()

    subscriptions = db.execute(
        select(Subscription).where(Subscription.author_id == current_user.id)
    ).scalars().all()

    for article in imported_articles:
        db.refresh(article)

        for subscription in subscriptions:
            notification = Notification(
                user_id=subscription.subscriber_id,
                article_id=article.id,
                message=f"New article published by {current_user.username}: {article.title}",
                is_read=False
            )
            db.add(notification)

    db.commit()

    return {"imported_count": len(imported_articles)}


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.execute(
        select(Article).where(Article.id == article_id)
    ).scalar_one_or_none()

    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    article = db.execute(
        select(Article).where(Article.id == article_id)
    ).scalar_one_or_none()

    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if article_data.title is not None:
        article.title = article_data.title

    if article_data.content is not None:
        article.content = article_data.content

    db.commit()
    db.refresh(article)

    return article


@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    article = db.execute(
        select(Article).where(Article.id == article_id)
    ).scalar_one_or_none()

    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(article)
    db.commit()

    return {"message": "Article deleted"}