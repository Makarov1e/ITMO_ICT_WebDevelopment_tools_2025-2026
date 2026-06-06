"""Роутер пользователей: профиль, список, смена пароля."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.core.security import verify_password
from app.crud import user as user_crud
from app.models.user import UserRole
from app.schemas.user import PasswordChange, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> UserRead:
    """Информация о текущем пользователе (по JWT)."""
    return current_user


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(data: PasswordChange, current_user: CurrentUser, session: SessionDep) -> None:
    """Смена пароля текущего пользователя."""
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Старый пароль неверен")
    user_crud.set_password(session, current_user, data.new_password)


@router.get("", response_model=list[UserRead])
def list_users(
    current_user: CurrentUser,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> list[UserRead]:
    """Список пользователей (требуется авторизация)."""
    return user_crud.list_users(session, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, current_user: CurrentUser, session: SessionDep) -> UserRead:
    """Информация о пользователе по id."""
    user = user_crud.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> UserRead:
    """Обновление профиля: доступно самому пользователю или администратору."""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    user = user_crud.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    # Менять роль может только администратор
    if data.role is not None and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Роль может менять только администратор")
    return user_crud.update_user(session, user, data)
