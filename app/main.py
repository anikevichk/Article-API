from fastapi import FastAPI, Depends, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import Base, get_db, engine
from app.routers import auth, users, articles, subscriptions, notifications

from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    integrity_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)


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
