"""Скрипт наполнения БД демо-данными.

Запуск:  python seed.py
Идемпотентен: повторный запуск не создаёт дубликатов.
"""
from datetime import datetime

from sqlmodel import Session, select

from app.core.database import engine
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.task import Tag, Task, TaskResourceLink
from app.models.team import Team, TeamMember
from app.models.solution import Solution, SolutionStatus, Evaluation


def get_or_create_user(s: Session, username: str, password: str, role: UserRole,
                       full_name: str, organization: str = "") -> User:
    user = s.exec(select(User).where(User.username == username)).first()
    if user:
        return user
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=hash_password(password),
        role=role,
        full_name=full_name,
        organization=organization,
    )
    s.add(user)
    s.commit()
    s.refresh(user)
    return user


def get_or_create_tag(s: Session, name: str) -> Tag:
    tag = s.exec(select(Tag).where(Tag.name == name)).first()
    if tag:
        return tag
    tag = Tag(name=name)
    s.add(tag)
    s.commit()
    s.refresh(tag)
    return tag


def main() -> None:
    with Session(engine) as s:
        # --- Пользователи ---
        admin = get_or_create_user(s, "admin", "admin12345", UserRole.ADMIN, "Главный администратор", "ИТМО")
        jury1 = get_or_create_user(s, "jury1", "jury12345", UserRole.JURY, "Ирина Соколова", "ИТМО")
        jury2 = get_or_create_user(s, "jury2", "jury12345", UserRole.JURY, "Павел Кузнецов", "Яндекс")
        jury3 = get_or_create_user(s, "jury3", "jury12345", UserRole.JURY, "Мария Орлова", "Сбер")
        cur1 = get_or_create_user(s, "curator1", "curator12345", UserRole.CURATOR, "Алексей Морозов", "ИТМО")
        cur2 = get_or_create_user(s, "curator2", "curator12345", UserRole.CURATOR, "Дмитрий Волков", "VK")
        cap1 = get_or_create_user(s, "captain1", "captain12345", UserRole.CAPTAIN, "Егор Макаров", "ИТМО")
        cap2 = get_or_create_user(s, "captain2", "captain12345", UserRole.CAPTAIN, "Анна Лебедева", "ИТМО")
        cap3 = get_or_create_user(s, "captain3", "captain12345", UserRole.CAPTAIN, "Никита Зайцев", "ИТМО")

        # --- Теги ---
        tags = {n: get_or_create_tag(s, n) for n in
                ["Python", "Django", "Vue.js", "ML", "Computer Vision", "NLP", "DevOps", "PostgreSQL"]}

        # --- Задачи ---
        def ensure_task(title, description, curator, tag_names, links, consultation):
            task = s.exec(select(Task).where(Task.title == title)).first()
            if task:
                return task
            task = Task(title=title, description=description, consultation_url=consultation,
                        curator_id=curator.id if curator else None)
            task.tags = [tags[t] for t in tag_names]
            task.resource_links = [TaskResourceLink(title=lt, url=lu) for lt, lu in links]
            s.add(task)
            s.commit()
            s.refresh(task)
            return task

        t1 = ensure_task("Система рекомендаций для онлайн-магазина",
                         "Рекомендательная система на основе истории покупок.", cur1,
                         ["Python", "ML", "PostgreSQL"],
                         [("Датасет покупок", "https://example.com/dataset"),
                          ("Документация API", "https://example.com/docs")],
                         "https://meet.example.com/rec")
        t2 = ensure_task("Веб-платформа для волонтёров",
                         "Платформа, объединяющая волонтёров и организации.", cur2,
                         ["Django", "Vue.js", "DevOps"],
                         [("Макеты Figma", "https://figma.com/file/x")],
                         "https://meet.example.com/vol")
        t3 = ensure_task("Распознавание дорожных знаков",
                         "Модель компьютерного зрения для распознавания знаков.", None,
                         ["Python", "Computer Vision", "ML"],
                         [("Набор изображений", "https://example.com/signs")],
                         "https://meet.example.com/cv")

        # --- Команды ---
        def ensure_team(name, motto, captain, task, members):
            team = s.exec(select(Team).where(Team.name == name)).first()
            if team:
                return team
            team = Team(name=name, motto=motto, captain_id=captain.id,
                        selected_task_id=task.id if task else None)
            team.members = [TeamMember(full_name=fn, role_in_team=r) for fn, r in members]
            s.add(team)
            s.commit()
            s.refresh(team)
            return team

        team1 = ensure_team("CodeStorm", "Код, который меняет мир", cap1, t1,
                            [("Егор Макаров", "Капитан, Backend"), ("Ольга Петрова", "ML"), ("Иван Сидоров", "Frontend")])
        team2 = ensure_team("PixelForce", "Видим больше", cap2, t3,
                            [("Анна Лебедева", "Капитан, CV"), ("Сергей Новиков", "ML"), ("Юлия Козлова", "Data")])
        team3 = ensure_team("GreenHands", "Помогаем вместе", cap3, t2,
                            [("Никита Зайцев", "Капитан, Fullstack"), ("Дарья Михайлова", "Designer")])

        # --- Решения ---
        def ensure_solution(team, task, title, description, repo, status):
            sol = s.exec(select(Solution).where(Solution.title == title)).first()
            if sol:
                return sol
            sol = Solution(team_id=team.id, task_id=task.id, title=title, description=description,
                           repo_url=repo, status=status,
                           submitted_at=datetime.utcnow() if status == SolutionStatus.SUBMITTED else None)
            s.add(sol)
            s.commit()
            s.refresh(sol)
            return sol

        sol1 = ensure_solution(team1, t1, "RecoEngine", "Гибридная рекомендательная система.",
                               "https://github.com/example/recoengine", SolutionStatus.SUBMITTED)
        sol2 = ensure_solution(team2, t3, "SignNet", "CNN-модель, точность 96%.",
                               "https://github.com/example/signnet", SolutionStatus.SUBMITTED)
        ensure_solution(team3, t2, "VolunteerHub", "Платформа на Django + Vue.",
                        "https://github.com/example/volunteerhub", SolutionStatus.DRAFT)

        # --- Оценки ---
        def ensure_eval(sol, jury, score, comment):
            ex = s.exec(select(Evaluation).where(
                Evaluation.solution_id == sol.id, Evaluation.jury_member_id == jury.id)).first()
            if ex:
                return ex
            ev = Evaluation(solution_id=sol.id, jury_member_id=jury.id, score=score, comment=comment)
            s.add(ev)
            s.commit()
            return ev

        ensure_eval(sol1, jury1, 9, "Отличная проработка.")
        ensure_eval(sol1, jury2, 8, "Сильно, но мало тестов.")
        ensure_eval(sol1, jury3, 9, "Чистый код.")
        ensure_eval(sol2, jury1, 10, "Впечатляющая точность.")
        ensure_eval(sol2, jury2, 9, "Отличный результат.")
        ensure_eval(sol2, jury3, 8, "Медленный инференс.")

        # --- Итоги ---
        print("Пользователи:", s.exec(select(User)).all().__len__())
        print("Теги:", len(s.exec(select(Tag)).all()))
        print("Задачи:", len(s.exec(select(Task)).all()))
        print("Команды:", len(s.exec(select(Team)).all()))
        print("Участники:", len(s.exec(select(TeamMember)).all()))
        print("Решения:", len(s.exec(select(Solution)).all()))
        print("Оценки:", len(s.exec(select(Evaluation)).all()))


if __name__ == "__main__":
    main()
