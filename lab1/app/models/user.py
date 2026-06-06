"""ORM-модель пользователя и перечисление ролей."""

import enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.team import Team
    from app.models.solution import Evaluation


class UserRole(str, enum.Enum):
    """Роли пользователей системы хакатона."""
    ADMIN = "ADMIN"      # Главный администратор
    JURY = "JURY"        # Жюри
    CURATOR = "CURATOR"  # Куратор задачи
    CAPTAIN = "CAPTAIN"  # Капитан команды


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=150)
    email: str = Field(default="", max_length=255)
    hashed_password: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.CAPTAIN)
    full_name: str = Field(default="", max_length=255)
    organization: str = Field(default="", max_length=255)
    is_active: bool = Field(default=True)

    # one-to-many / one-to-one связи
    curated_task: Optional["Task"] = Relationship(back_populates="curator")
    team: Optional["Team"] = Relationship(back_populates="captain")
    evaluations_given: list["Evaluation"] = Relationship(back_populates="jury_member")
