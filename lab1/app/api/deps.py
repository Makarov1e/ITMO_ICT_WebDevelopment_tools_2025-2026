"""Зависимости FastAPI: сессия БД и ручная аутентификация по JWT.

Аутентификация (п.3 задания) реализована вручную: мы сами читаем заголовок
Authorization, парсим схему Bearer, проверяем токен нашим декодером и
достаём пользователя из БД. Сторонние библиотеки безопасности не используются.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import JWTError, decode_access_token
from app.models.user import User, UserRole

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """Извлекает и проверяет JWT из заголовка Authorization, возвращает пользователя."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise credentials_error

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise credentials_error
    token = parts[1]

    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error

    user = session.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    """Фабрика зависимостей: пропускает только пользователей с нужной ролью."""
    def checker(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции",
            )
        return current_user
    return checker
