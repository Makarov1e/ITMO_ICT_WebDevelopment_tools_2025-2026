"""Импорт всех ORM-моделей, чтобы метаданные SQLModel/Alembic видели таблицы."""
from app.models.user import User, UserRole
from app.models.task import Task, Tag, TaskTagLink, TaskResourceLink
from app.models.team import Team, TeamMember
from app.models.solution import Solution, SolutionStatus, Evaluation

__all__ = [
    "User", "UserRole",
    "Task", "Tag", "TaskTagLink", "TaskResourceLink",
    "Team", "TeamMember",
    "Solution", "SolutionStatus", "Evaluation",
]
