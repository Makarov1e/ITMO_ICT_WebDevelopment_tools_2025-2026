"""Роутер аутентификации: регистрация, вход и выдача JWT."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.core.security import create_access_token, verify_password
from app.crud import user as user_crud
from app.schemas.user import LoginRequest, Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: SessionDep) -> UserRead:
    """Регистрация нового пользователя."""
    if user_crud.get_user_by_username(session, data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким username уже существует",
        )
    user = user_crud.create_user(session, data)
    return user


@router.post("/login", response_model=Token)
def login(data: LoginRequest, session: SessionDep) -> Token:
    """Авторизация по username/паролю с выдачей JWT-токена."""
    user = user_crud.get_user_by_username(session, data.username)
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь заблокирован")

    token = create_access_token(subject=user.id, extra={"role": user.role.value})
    return Token(access_token=token)
