"""CRUD-операции для решений и оценок жюри."""
from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from app.models.solution import Evaluation, Solution, SolutionStatus
from app.schemas.solution import EvaluationCreate, SolutionCreate, SolutionUpdate


def get_solution(session: Session, solution_id: int) -> Solution | None:
    return session.get(Solution, solution_id)


def list_solutions(session: Session, skip: int = 0, limit: int = 100) -> list[Solution]:
    return list(session.exec(select(Solution).offset(skip).limit(limit)).all())


def create_solution(session: Session, data: SolutionCreate) -> Solution:
    solution = Solution(**data.model_dump())
    if solution.status == SolutionStatus.SUBMITTED:
        solution.submitted_at = datetime.utcnow()
    session.add(solution)
    session.commit()
    session.refresh(solution)
    return solution


def update_solution(session: Session, solution: Solution, data: SolutionUpdate) -> Solution:
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(solution, field, value)
    # Проставляем время отправки при переходе в статус SUBMITTED
    if payload.get("status") == SolutionStatus.SUBMITTED and solution.submitted_at is None:
        solution.submitted_at = datetime.utcnow()
    session.add(solution)
    session.commit()
    session.refresh(solution)
    return solution


def delete_solution(session: Session, solution: Solution) -> None:
    session.delete(solution)
    session.commit()


def avg_score(solution: Solution) -> float | None:
    """Средний балл по оценкам решения (или None, если оценок нет)."""
    evals = solution.evaluations
    if not evals:
        return None
    return round(sum(e.score for e in evals) / len(evals), 2)


# --- Evaluations ---
def create_evaluation(session: Session, data: EvaluationCreate, jury_member_id: int) -> Evaluation:
    evaluation = Evaluation(
        solution_id=data.solution_id,
        jury_member_id=jury_member_id,
        score=data.score,
        comment=data.comment,
    )
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)
    return evaluation
