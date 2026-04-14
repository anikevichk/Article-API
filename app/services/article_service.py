from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models import Article, Subscription, User, Notification
from app.schemas import ArticleCreate, ArticleUpdate
from app.services.notification_service import notify_subscribers_about_articles


def list_articles_service(db: Session) -> list[Article]:
    result = db.execute(select(Article).order_by(Article.id.desc()))
    return result.scalars().all()


def get_my_articles_service(db: Session, current_user: User) -> list[Article]:
    articles = db.execute(
        select(Article)
        .where(Article.author_id == current_user.id)
        .order_by(Article.id.desc())
    )
    return articles.scalars().all()


def get_subscribed_articles_service(
    db: Session, current_user: User
) -> list[Article]:
    author_ids = (
        db.execute(
            select(Subscription.author_id).where(
                Subscription.subscriber_id == current_user.id
            )
        )
        .scalars()
        .all()
    )

    if not author_ids:
        return []

    articles = db.execute(
        select(Article)
        .where(Article.author_id.in_(author_ids))
        .order_by(Article.id.desc())
    )
    return articles.scalars().all()


def get_article_service(db: Session, article_id: int) -> Article:
    article = db.execute(
        select(Article).where(Article.id == article_id)
    ).scalar_one_or_none()

    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


def create_article_service(
    db: Session,
    current_user: User,
    article_data: ArticleCreate,
) -> Article:
    article = Article(
        title=article_data.title,
        content=article_data.content,
        author_id=current_user.id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    notify_subscribers_about_articles(db, current_user, [article])
    return article


def update_article_service(
    db: Session,
    current_user: User,
    article_id: int,
    article_data: ArticleUpdate,
) -> Article:
    article = get_article_service(db, article_id)

    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if article_data.title is not None:
        article.title = article_data.title

    if article_data.content is not None:
        article.content = article_data.content

    db.commit()
    db.refresh(article)

    return article


def delete_article_service(
    db: Session,
    current_user: User,
    article_id: int,
) -> dict[str, str]:
    article = get_article_service(db, article_id)

    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.execute(
        delete(Notification).where(Notification.article_id == article.id)
    )

    db.delete(article)
    db.commit()

    return {"message": "Article deleted"}
