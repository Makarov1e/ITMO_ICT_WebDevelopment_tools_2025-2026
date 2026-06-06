"""Роутер команд (CRUD + GET с вложенными участниками)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.crud import team as team_crud
from app.schemas.team import (
    TeamCreate,
    TeamMemberCreate,
    TeamMemberRead,
    TeamRead,
    TeamUpdate,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamRead])
def list_teams(current_user: CurrentUser, session: SessionDep, skip: int = 0, limit: int = 100):
    return team_crud.list_teams(session, skip=skip, limit=limit)


@router.get("/{team_id}", response_model=TeamRead)
def get_team(team_id: int, current_user: CurrentUser, session: SessionDep):
    team = team_crud.get_team(session, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")
    return team


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(data: TeamCreate, current_user: CurrentUser, session: SessionDep):
    return team_crud.create_team(session, data)


@router.patch("/{team_id}", response_model=TeamRead)
def update_team(team_id: int, data: TeamUpdate, current_user: CurrentUser, session: SessionDep):
    team = team_crud.get_team(session, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")
    return team_crud.update_team(session, team, data)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, current_user: CurrentUser, session: SessionDep):
    team = team_crud.get_team(session, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")
    team_crud.delete_team(session, team)


@router.post("/{team_id}/members", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED)
def add_member(team_id: int, data: TeamMemberCreate, current_user: CurrentUser, session: SessionDep):
    team = team_crud.get_team(session, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")
    return team_crud.add_member(session, team, data)
