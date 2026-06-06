"""CRUD-операции для пользователей."""
from __future__ import annotations

from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()


def list_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return list(session.exec(select(User).offset(skip).limit(limit)).all())


def create_user(session: Session, data: UserCreate) -> User:
    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        organization=data.organization,
        role=data.role,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def set_password(session: Session, user: User, new_password: str) -> User:
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
