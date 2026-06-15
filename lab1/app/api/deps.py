"""Зависимости FastAPI: сессия БД и ручная аутентификация по JWT.

Аутентификация (п.3 задания) реализована вручную: проверку подписи и срока
действия токена выполняет наш собственный `decode_access_token` (без сторонних
JWT/security-библиотек). Схема `HTTPBearer` используется только для того, чтобы
в Swagger появилась кнопка «Authorize» и токен извлекался из заголовка — сама
валидация JWT остаётся ручной.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import JWTError, decode_access_token
from app.models.user import User, UserRole

SessionDep = Annotated[Session, Depends(get_session)]

# Схема Bearer для Swagger (кнопка Authorize). auto_error=False — ошибку
# отсутствия токена обрабатываем сами, единообразно.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> User:
    """Извлекает и проверяет JWT из заголовка Authorization, возвращает пользователя."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_error
    token = credentials.credentials

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
