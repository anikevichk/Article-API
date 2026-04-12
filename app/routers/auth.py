from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models import User
from app.schemas import UserRegister, UserResponse, TokenResponse
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user_by_email = db.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()

    if existing_user_by_email:
        raise HTTPException(status_code=409, detail="Email already registered")

    existing_user_by_username = db.execute(
        select(User).where(User.username == user_data.username)
    ).scalar_one_or_none()

    if existing_user_by_username:
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.username == form_data.username)
    ).scalar_one_or_none()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }