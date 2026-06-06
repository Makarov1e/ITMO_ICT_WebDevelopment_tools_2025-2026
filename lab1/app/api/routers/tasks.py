"""Роутер задач и тегов (CRUD + GET с вложенными объектами)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, SessionDep, require_roles
from app.crud import task as task_crud
from app.models.user import User, UserRole
from app.schemas.task import (
    TagCreate,
    TagRead,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Создавать/изменять задачи может только администратор
admin_only = require_roles(UserRole.ADMIN)


@router.get("", response_model=list[TaskRead])
def list_tasks(current_user: CurrentUser, session: SessionDep, skip: int = 0, limit: int = 100):
    return task_crud.list_tasks(session, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, current_user: CurrentUser, session: SessionDep):
    task = task_crud.get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, session: SessionDep, _: User = Depends(admin_only)):
    return task_crud.create_task(session, data)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, data: TaskUpdate, session: SessionDep, _: User = Depends(admin_only)):
    task = task_crud.get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task_crud.update_task(session, task, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: SessionDep, _: User = Depends(admin_only)):
    task = task_crud.get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    task_crud.delete_task(session, task)


# --- Tags ---
@router.get("/tags/all", response_model=list[TagRead])
def list_tags(current_user: CurrentUser, session: SessionDep):
    return task_crud.list_tags(session)


@router.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(data: TagCreate, session: SessionDep, _: User = Depends(admin_only)):
    return task_crud.create_tag(session, data)
