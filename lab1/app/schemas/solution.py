"""Pydantic-схемы решений и оценок жюри."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.solution import SolutionStatus
from app.schemas.task import TaskBrief
from app.schemas.team import TeamBrief
from app.schemas.user import UserRead


# --- Evaluation ---
class EvaluationCreate(BaseModel):
    solution_id: int
    score: int = Field(ge=0, le=10)
    comment: str = ""


class EvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    score: int
    comment: str
    created_at: datetime
    jury_member: UserRead | None = None


# --- Solution ---
class SolutionCreate(BaseModel):
    title: str
    description: str = ""
    repo_url: str = ""
    team_id: int
    task_id: int
    status: SolutionStatus = SolutionStatus.DRAFT


class SolutionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    repo_url: str | None = None
    status: SolutionStatus | None = None


class SolutionRead(BaseModel):
    """Решение с вложенными командой, задачей и списком оценок (one-to-many)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    repo_url: str
    status: SolutionStatus
    created_at: datetime
    submitted_at: datetime | None = None
    team: TeamBrief | None = None
    task: TaskBrief | None = None
    evaluations: list[EvaluationRead] = []
    avg_score: float | None = None
