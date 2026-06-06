"""Pydantic-схемы пользователя и аутентификации (вход/выход API)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Данные для регистрации пользователя."""
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=4, max_length=128)
    email: str = ""
    full_name: str = ""
    organization: str = ""
    role: UserRole = UserRole.CAPTAIN


class UserUpdate(BaseModel):
    """Частичное обновление профиля пользователя."""
    email: str | None = None
    full_name: str | None = None
    organization: str | None = None
    role: UserRole | None = None


class UserRead(BaseModel):
    """Публичное представление пользователя (без пароля)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: UserRole
    full_name: str
    organization: str
    is_active: bool


class PasswordChange(BaseModel):
    """Смена пароля текущего пользователя."""
    old_password: str
    new_password: str = Field(min_length=4, max_length=128)


class LoginRequest(BaseModel):
    """Тело запроса на авторизацию."""
    username: str
    password: str


class Token(BaseModel):
    """Ответ с JWT-токеном."""
    access_token: str
    token_type: str = "bearer"
