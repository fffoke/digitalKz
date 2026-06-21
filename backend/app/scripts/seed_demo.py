"""Демо-данные для теста всей платформы.

Запуск (в контейнере backend):
    python -m app.scripts.seed_demo

Создаёт:
  admin@gmail.com    — администратор (для админки на :5174)
  teacher@gmail.com  — преподаватель (ведёт демо-группу)
  user1@gmail.com    — ученик (уровень B1)
  user2@gmail.com    — ученик (уровень B1)
Пароль у всех: password123

Плюс: демо-группа B1 с обоими учениками и преподавателем, активный урок
(Jitsi), домашние задания, учебный материал, вступительный и level-экзамены,
пара сообщений в чате группы.
"""
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.db.enums import (
    ExamType,
    HomeworkStatus,
    LanguageLevel,
    LessonStatus,
    Rank,
    Role,
    Schedule,
)
from app.db.models.content import Exam, Material
from app.db.models.learning import Group, GroupMember, GroupMessage, Homework, Lesson
from app.db.models.user import User
from app.db.repositories.user import UserRepository
from app.db.session import SessionLocal
from app.services.learning import LearningService

PASSWORD = "password123"


def get_or_create_user(db, *, email, name, role, level=None, rank=None) -> User:
    user = UserRepository(db).get_by_email(email)
    if user is None:
        user = User(name=name, email=email, password_hash=hash_password(PASSWORD))
        db.add(user)
    user.name = name
    user.password_hash = hash_password(PASSWORD)  # гарантируем демо-пароль
    user.role = role
    user.level = level
    user.rank = rank
    user.is_verified = role in (Role.student, Role.teacher)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main() -> None:
    db = SessionLocal()
    svc = LearningService(db)
    try:
        svc._ensure_plan()

        admin = get_or_create_user(db, email="admin@gmail.com", name="Админ", role=Role.admin)
        teacher = get_or_create_user(db, email="teacher@gmail.com", name="Айбек Мұғалім", role=Role.teacher)
        u1 = get_or_create_user(db, email="user1@gmail.com", name="Аружан", role=Role.student, level=LanguageLevel.B1, rank=Rank.orta)
        u2 = get_or_create_user(db, email="user2@gmail.com", name="Бекзат", role=Role.student, level=LanguageLevel.B1, rank=Rank.orta)

        # --- демо-группа B1 ---
        group = db.query(Group).filter(Group.name == "Демо-поток B1").first()
        if group is None:
            group = Group(
                name="Демо-поток B1", level=LanguageLevel.B1, schedule=Schedule.three_week,
                invite_code="demo-b1", teacher_id=teacher.id,
                current_section=1, current_stage=1,
            )
            db.add(group)
            db.flush()
            svc._init_group_progress(group)
        group.teacher_id = teacher.id
        db.commit()

        # всегда гарантируем членство обоих учеников (идемпотентно)
        for student in (u1, u2):
            if db.get(GroupMember, {"group_id": group.id, "user_id": student.id}) is None:
                db.add(GroupMember(group_id=group.id, user_id=student.id))
        db.commit()

        # --- активный урок (через 2 часа → попадает в окно 6ч, чат открыт) ---
        if not db.query(Lesson).filter(Lesson.group_id == group.id).first():
            db.add(Lesson(
                group_id=group.id, teacher_id=teacher.id,
                starts_at=datetime.now(timezone.utc) + timedelta(hours=2),
                zoom_link=svc._meeting_link(), status=LessonStatus.open,
            ))

        # --- домашние задания обоим ученикам ---
        for student in (u1, u2):
            if not db.query(Homework).filter(Homework.group_id == group.id, Homework.student_id == student.id).first():
                db.add(Homework(
                    group_id=group.id, student_id=student.id,
                    task="Составьте 5 фраз о своём дне на казахском и короткий диалог в кафе.",
                    status=HomeworkStatus.assigned,
                ))

        # --- учебный материал ---
        if not db.query(Material).filter(Material.title == "B1: Разговор в кафе").first():
            db.add(Material(
                level=LanguageLevel.B1, section=1, stage=1,
                title="B1: Разговор в кафе",
                content="Лексика: мәзір (меню), тапсырыс (заказ), есеп (счёт). "
                        "Фразы: «Маған кофе беріңізші», «Есеп әкеліңізші».",
                author_id=admin.id,
            ))

        # --- вступительный экзамен (вопросы) ---
        entrance = db.query(Exam).filter(Exam.type == ExamType.entrance).first()
        if entrance is None:
            entrance = Exam(title="Вступительный тест", type=ExamType.entrance,
                            questions=[], voice_task="Прочитайте текст на казахском вслух.")
            db.add(entrance)
        entrance.questions = [
            {"type": "choice", "text": "«Сәлеметсіз бе» дегеніміз не?",
             "options": ["Здравствуйте", "Спасибо", "Пока"], "answer": "Здравствуйте"},
            {"type": "choice", "text": "«Рахмет» аудармасы?",
             "options": ["Привет", "Спасибо", "Да"], "answer": "Спасибо"},
        ]

        # --- экзамен на повышение до B2 ---
        if not db.query(Exam).filter(Exam.type == ExamType.level, Exam.target_level == LanguageLevel.B2).first():
            db.add(Exam(
                title="Экзамен на B2", type=ExamType.level, target_level=LanguageLevel.B2,
                voice_task="Расскажите голосом о своём рабочем дне на казахском (3–4 предложения).",
                questions=[
                    {"type": "choice", "text": "«Жұмыс» дегеніміз?",
                     "options": ["Отдых", "Работа", "Дом"], "answer": "Работа"},
                    {"type": "listening", "text": "Послушайте и напишите услышанное",
                     "options": [], "answer": "Сәлеметсіз бе", "audio_url": ""},
                ],
            ))

        # --- сообщения в чате группы ---
        if not db.query(GroupMessage).filter(GroupMessage.group_id == group.id).first():
            db.add(GroupMessage(group_id=group.id, sender_id=teacher.id,
                                text="Сәлеметсіздер ме! Бүгінгі сабаққа дайынсыздар ма?"))
            db.add(GroupMessage(group_id=group.id, sender_id=u1.id,
                                text="Иә, дайынмын!"))

        db.commit()
        print("✅ Демо-данные готовы.")
        print("   admin@gmail.com / teacher@gmail.com / user1@gmail.com / user2@gmail.com")
        print(f"   Пароль у всех: {PASSWORD}")
        print(f"   Группа: {group.name} (код demo-b1), преподаватель teacher@gmail.com")
    finally:
        db.close()


if __name__ == "__main__":
    main()
