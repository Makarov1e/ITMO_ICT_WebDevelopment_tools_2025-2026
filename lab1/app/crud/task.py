"""CRUD-операции для задач и тегов."""
from __future__ import annotations

from sqlmodel import Session, select

from app.models.task import Tag, Task, TaskResourceLink
from app.schemas.task import TagCreate, TaskCreate, TaskUpdate


# --- Tags ---
def list_tags(session: Session) -> list[Tag]:
    return list(session.exec(select(Tag)).all())


def create_tag(session: Session, data: TagCreate) -> Tag:
    tag = Tag(name=data.name)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


# --- Tasks ---
def get_task(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)


def list_tasks(session: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    return list(session.exec(select(Task).offset(skip).limit(limit)).all())


def _resolve_tags(session: Session, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []
    return list(session.exec(select(Tag).where(Tag.id.in_(tag_ids))).all())


def create_task(session: Session, data: TaskCreate) -> Task:
    task = Task(
        title=data.title,
        description=data.description,
        consultation_url=data.consultation_url,
        curator_id=data.curator_id,
    )
    task.tags = _resolve_tags(session, data.tag_ids)
    task.resource_links = [
        TaskResourceLink(title=link.title, url=link.url) for link in data.resource_links
    ]
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task(session: Session, task: Task, data: TaskUpdate) -> Task:
    payload = data.model_dump(exclude_unset=True)
    tag_ids = payload.pop("tag_ids", None)
    for field, value in payload.items():
        setattr(task, field, value)
    if tag_ids is not None:
        task.tags = _resolve_tags(session, tag_ids)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task: Task) -> None:
    session.delete(task)
    session.commit()
