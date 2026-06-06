"""Pydantic-схемы задач, тегов и ресурсных ссылок."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserRead


# --- Tag ---
class TagCreate(BaseModel):
    name: str


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


# --- Resource link ---
class TaskResourceLinkCreate(BaseModel):
    title: str
    url: str


class TaskResourceLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    url: str


# --- Task ---
class TaskCreate(BaseModel):
    title: str
    description: str = ""
    consultation_url: str = ""
    curator_id: int | None = None
    tag_ids: list[int] = []
    resource_links: list[TaskResourceLinkCreate] = []


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    consultation_url: str | None = None
    curator_id: int | None = None
    tag_ids: list[int] | None = None


class TaskBrief(BaseModel):
    """Краткое представление задачи для вложений в другие схемы."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


class TaskRead(BaseModel):
    """Полное представление задачи с вложенными объектами."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    consultation_url: str
    created_at: datetime
    curator: UserRead | None = None
    tags: list[TagRead] = []
    resource_links: list[TaskResourceLinkRead] = []
