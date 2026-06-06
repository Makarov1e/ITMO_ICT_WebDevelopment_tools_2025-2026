"""Роутер решений и оценок жюри (CRUD + вложенные оценки + средний балл)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, SessionDep, require_roles
from app.crud import solution as solution_crud
from app.models.solution import Solution
from app.models.user import User, UserRole
from app.schemas.solution import (
    EvaluationCreate,
    EvaluationRead,
    SolutionCreate,
    SolutionRead,
    SolutionUpdate,
)

router = APIRouter(prefix="/solutions", tags=["solutions"])

# Оценивать решения могут только жюри
jury_only = require_roles(UserRole.JURY)


def _to_read(solution: Solution) -> SolutionRead:
    """Собирает схему решения и добавляет вычисляемый средний балл."""
    read = SolutionRead.model_validate(solution)
    read.avg_score = solution_crud.avg_score(solution)
    return read


@router.get("", response_model=list[SolutionRead])
def list_solutions(current_user: CurrentUser, session: SessionDep, skip: int = 0, limit: int = 100):
    return [_to_read(s) for s in solution_crud.list_solutions(session, skip=skip, limit=limit)]


@router.get("/{solution_id}", response_model=SolutionRead)
def get_solution(solution_id: int, current_user: CurrentUser, session: SessionDep):
    solution = solution_crud.get_solution(session, solution_id)
    if solution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Решение не найдено")
    return _to_read(solution)


@router.post("", response_model=SolutionRead, status_code=status.HTTP_201_CREATED)
def create_solution(data: SolutionCreate, current_user: CurrentUser, session: SessionDep):
    return _to_read(solution_crud.create_solution(session, data))


@router.patch("/{solution_id}", response_model=SolutionRead)
def update_solution(solution_id: int, data: SolutionUpdate, current_user: CurrentUser, session: SessionDep):
    solution = solution_crud.get_solution(session, solution_id)
    if solution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Решение не найдено")
    return _to_read(solution_crud.update_solution(session, solution, data))


@router.delete("/{solution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_solution(solution_id: int, current_user: CurrentUser, session: SessionDep):
    solution = solution_crud.get_solution(session, solution_id)
    if solution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Решение не найдено")
    solution_crud.delete_solution(session, solution)


@router.post("/{solution_id}/evaluations", response_model=EvaluationRead, status_code=status.HTTP_201_CREATED)
def evaluate(
    solution_id: int,
    data: EvaluationCreate,
    session: SessionDep,
    jury: User = Depends(jury_only),
):
    """Оценка решения членом жюри (один член жюри — одна оценка на решение)."""
    solution = solution_crud.get_solution(session, solution_id)
    if solution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Решение не найдено")
    data.solution_id = solution_id
    try:
        return solution_crud.create_evaluation(session, data, jury_member_id=jury.id)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже оценивали это решение",
        ) from exc
