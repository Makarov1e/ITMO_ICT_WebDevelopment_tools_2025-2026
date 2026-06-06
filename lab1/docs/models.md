# Модели (ORM SQLModel)

Все таблицы описаны через SQLModel и хранятся в PostgreSQL. Исходники:
[`app/models/`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/lab1/app/models).

## Связи между сущностями

| Тип связи | Пример |
|---|---|
| **many-to-many** | `Task` ↔ `Tag` (через `TaskTagLink`) |
| **one-to-many** | `Team` → `TeamMember`, `Solution` → `Evaluation`, `Task` → `TaskResourceLink` |
| **one-to-one** | `Task.curator` → `User`, `Team.captain` → `User` |
| **many-to-one** | `Team.selected_task` → `Task`, `Solution.task` → `Task` |

## `app/models/user.py`

```python
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
```

## `app/models/task.py`

```python
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
```

## `app/models/team.py`

```python
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
```

## `app/models/solution.py`

```python
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
```
