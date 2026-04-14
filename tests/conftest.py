import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db
from app.models import Base


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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
    register_response = register_user(
        client, email=email, username=username, password=password
    )
    assert register_response.status_code in (200, 201), register_response.text

    response = login_user(client, username=username, password=password)
    assert response.status_code == 200, response.text

    return response.json()["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}