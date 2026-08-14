from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def register_user(db: Session, user_in: UserCreate) -> User:
    # 1. Check if user with email already exists
    stmt = select(User).where(User.email == user_in.email)
    existing_user = db.scalar(stmt)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # 2. Hash password and create user instance
    db_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )

    # 3. Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = db.scalar(stmt)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
