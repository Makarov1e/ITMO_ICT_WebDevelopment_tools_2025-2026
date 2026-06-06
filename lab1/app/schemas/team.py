"""Pydantic-схемы команд и участников."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.task import TaskBrief
from app.schemas.user import UserRead


# --- Team member ---
class TeamMemberCreate(BaseModel):
    full_name: str
    email: str = ""
    role_in_team: str = ""


class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: str
    role_in_team: str


# --- Team ---
class TeamCreate(BaseModel):
    name: str
    motto: str = ""
    captain_id: int
    selected_task_id: int | None = None
    members: list[TeamMemberCreate] = []


class TeamUpdate(BaseModel):
    name: str | None = None
    motto: str | None = None
    selected_task_id: int | None = None


class TeamBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TeamRead(BaseModel):
    """Команда с вложенными капитаном, задачей и участниками (one-to-many)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    motto: str
    created_at: datetime
    captain: UserRead | None = None
    selected_task: TaskBrief | None = None
    members: list[TeamMemberRead] = []
