from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Article, Notification, Subscription, User


def notify_subscribers_about_articles(
    db: Session,
    author: User,
    articles: list[Article],
) -> None:
    if not articles:
        return

    subscriptions = (
        db.execute(
            select(Subscription).where(Subscription.author_id == author.id)
        )
        .scalars()
        .all()
    )

    if not subscriptions:
        return

    for article in articles:
        if article.id is None:
            db.refresh(article)

        for subscription in subscriptions:
            notification = Notification(
                user_id=subscription.subscriber_id,
                article_id=article.id,
                message=(
                    f"New article published by {author.username}: "
                    f"{article.title}"
                ),
                is_read=False,
            )
            db.add(notification)

    db.commit()
