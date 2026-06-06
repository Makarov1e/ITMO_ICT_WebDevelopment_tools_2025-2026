"""ORM-модели решения команды и оценки жюри (one-to-many)."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task
    from app.models.team import Team


class SolutionStatus(str, enum.Enum):
    DRAFT = "DRAFT"          # Черновик
    SUBMITTED = "SUBMITTED"  # Отправлено


class Solution(SQLModel, table=True):
    __tablename__ = "solutions"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str = ""
    repo_url: str = Field(default="", max_length=500)
    status: SolutionStatus = Field(default=SolutionStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = Field(default=None)

    team_id: int = Field(foreign_key="teams.id")
    team: Optional["Team"] = Relationship(back_populates="solutions")

    task_id: int = Field(foreign_key="tasks.id")
    task: Optional["Task"] = Relationship(back_populates="solutions")

    # one-to-many: оценки жюри
    evaluations: list["Evaluation"] = Relationship(
        back_populates="solution",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Evaluation(SQLModel, table=True):
    """Оценка решения членом жюри. Уникальна по паре (решение, член жюри)."""
    __tablename__ = "evaluations"
    __table_args__ = (UniqueConstraint("solution_id", "jury_member_id", name="uq_evaluation_solution_jury"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    score: int = Field(ge=0, le=10)
    comment: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    solution_id: int = Field(foreign_key="solutions.id")
    solution: Optional["Solution"] = Relationship(back_populates="evaluations")

    jury_member_id: int = Field(foreign_key="users.id")
    jury_member: Optional["User"] = Relationship(back_populates="evaluations_given")
