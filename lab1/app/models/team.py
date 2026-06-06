"""ORM-модели команды и её участников (one-to-many)."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task
    from app.models.solution import Solution


class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    motto: str = Field(default="", max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # В системе регистрируется только капитан (one-to-one с User)
    captain_id: int = Field(foreign_key="users.id", unique=True)
    captain: Optional["User"] = Relationship(back_populates="team")

    # Команда выбирает одну задачу (many-to-one)
    selected_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    selected_task: Optional["Task"] = Relationship(back_populates="teams")

    # one-to-many: участники команды
    members: list["TeamMember"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # one-to-many: решения команды
    solutions: list["Solution"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TeamMember(SQLModel, table=True):
    """Участник команды (не является пользователем системы)."""
    __tablename__ = "team_members"

    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id")
    full_name: str = Field(max_length=255)
    email: str = Field(default="", max_length=255)
    role_in_team: str = Field(default="", max_length=128)

    team: Optional["Team"] = Relationship(back_populates="members")
