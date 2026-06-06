"""CRUD-операции для команд и участников."""
from __future__ import annotations

from sqlmodel import Session, select

from app.models.team import Team, TeamMember
from app.schemas.team import TeamCreate, TeamMemberCreate, TeamUpdate


def get_team(session: Session, team_id: int) -> Team | None:
    return session.get(Team, team_id)


def list_teams(session: Session, skip: int = 0, limit: int = 100) -> list[Team]:
    return list(session.exec(select(Team).offset(skip).limit(limit)).all())


def create_team(session: Session, data: TeamCreate) -> Team:
    team = Team(
        name=data.name,
        motto=data.motto,
        captain_id=data.captain_id,
        selected_task_id=data.selected_task_id,
    )
    team.members = [
        TeamMember(full_name=m.full_name, email=m.email, role_in_team=m.role_in_team)
        for m in data.members
    ]
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


def update_team(session: Session, team: Team, data: TeamUpdate) -> Team:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


def delete_team(session: Session, team: Team) -> None:
    session.delete(team)
    session.commit()


def add_member(session: Session, team: Team, data: TeamMemberCreate) -> TeamMember:
    member = TeamMember(
        team_id=team.id,
        full_name=data.full_name,
        email=data.email,
        role_in_team=data.role_in_team,
    )
    session.add(member)
    session.commit()
    session.refresh(member)
    return member
