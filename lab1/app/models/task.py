"""ORM-модели задачи хакатона: Task, Tag (M2M), ресурсные ссылки (1-M)."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.team import Team
    from app.models.solution import Solution


class TaskTagLink(SQLModel, table=True):
    """Связующая таблица для many-to-many между Task и Tag."""
    __tablename__ = "task_tag_link"

    task_id: Optional[int] = Field(default=None, foreign_key="tasks.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=64)

    tasks: list["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str = ""
    consultation_url: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Куратор ведёт одну задачу (one-to-one): FK на пользователя, уникальный
    curator_id: Optional[int] = Field(default=None, foreign_key="users.id", unique=True)
    curator: Optional["User"] = Relationship(back_populates="curated_task")

    # many-to-many с тегами
    tags: list["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)

    # one-to-many: ресурсные ссылки
    resource_links: list["TaskResourceLink"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # one-to-many: команды, выбравшие эту задачу
    teams: list["Team"] = Relationship(back_populates="selected_task")

    # one-to-many: решения по этой задаче
    solutions: list["Solution"] = Relationship(back_populates="task")


class TaskResourceLink(SQLModel, table=True):
    """Ссылка-ресурс, прикреплённая к задаче (документация, датасет и т.п.)."""
    __tablename__ = "task_resource_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    title: str = Field(max_length=255)
    url: str = Field(max_length=500)

    task: Optional["Task"] = Relationship(back_populates="resource_links")
