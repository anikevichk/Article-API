from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.models import User, Subscription
from app.schemas import SubscriptionResponse
from app.security import get_current_user

router = APIRouter(prefix="/users", tags=["subscriptions"])


@router.post(
    "/{author_username}/subscribe", response_model=SubscriptionResponse
)
def subscribe_to_author(
    author_username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    author = db.execute(
        select(User).where(User.username == author_username)
    ).scalar_one_or_none()

    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    if current_user.id == author.id:
        raise HTTPException(
            status_code=400, detail="You cannot subscribe to yourself"
        )

    existing_subscription = db.execute(
        select(Subscription).where(
            Subscription.subscriber_id == current_user.id,
            Subscription.author_id == author.id,
        )
    ).scalar_one_or_none()

    if existing_subscription is not None:
        raise HTTPException(
            status_code=409, detail="Already subscribed to this author"
        )

    subscription = Subscription(
        subscriber_id=current_user.id, author_id=author.id
    )

    db.add(subscription)

    try:
        db.commit()
        db.refresh(subscription)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Already subscribed to this author"
        )
    
    return subscription


@router.delete("/{author_username}/subscribe")
def unsubscribe_from_author(
    author_username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    author = db.execute(
        select(User).where(User.username == author_username)
    ).scalar_one_or_none()

    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    subscription = db.execute(
        select(Subscription).where(
            Subscription.subscriber_id == current_user.id,
            Subscription.author_id == author.id,
        )
    ).scalar_one_or_none()

    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")

    db.delete(subscription)
    db.commit()

    return {"message": "Unsubscribed successfully"}
