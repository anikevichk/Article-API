import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db
from app.models import Base

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def register_user(
    client,
    email="user@example.com",
    username="user",
    password="12345678",
):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )


def login_user(client, username="user", password="12345678"):
    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )


def get_token(
    client,
    email="user@example.com",
    username="user",
    password="12345678",
):
    register_user(client, email=email, username=username, password=password)
    response = login_user(client, username=username, password=password)
    return response.json()["access_token"]