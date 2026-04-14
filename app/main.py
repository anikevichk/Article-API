from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.routers import auth, users, articles, subscriptions, notifications

app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(subscriptions.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {"message": "API works"}


@app.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}