"""Демо для преподавателя и отзывов.

Запуск:
    python -m app.scripts.seed_teacher_demo

- Несколько заявок на преподавателя (для модерации в админке).
- teacher@gmail.com снова ведёт «Демо-поток B1».
- Сданные ДЗ учеников — чтобы teacher@gmail.com их проверял.
- ДЗ для user1@gmail.com во всех статусах (сдать / на проверке / оценено).
- Завершённый урок, который user1 ещё НЕ оценил → можно написать отзыв педагогу.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import hash_password
from app.db.enums import (
    HomeworkStatus,
    LanguageLevel,
    LessonStatus,
    ModerationStatus,
    Role,
)
from app.db.models.learning import Group, GroupMember, Homework, Lesson, LessonRating
from app.db.models.user import TeacherApplication, User
from app.db.repositories.user import UserRepository
from app.db.session import SessionLocal
from app.services.learning import LearningService

PASSWORD = "password123"

APPLICANTS = [
    ("applicant1@gmail.com", "Сәуле Қажы", "КазНПУ им. Абая, казахская филология", "8 лет в школе"),
    ("applicant2@gmail.com", "Ерлан Тоқтар", "ЕНУ, лингвистика", "Репетитор, 4 года"),
    ("applicant3@gmail.com", "Гүлназ Серік", "КазНУ, журналистика", "Онлайн-курсы казахского, 3 года"),
]


def upsert(db, email, name, role=Role.user):
    u = UserRepository(db).get_by_email(email)
    if u is None:
        u = User(name=name, email=email, password_hash=hash_password(PASSWORD))
        db.add(u)
    u.name = name
    u.password_hash = hash_password(PASSWORD)
    db.add(u); db.commit(); db.refresh(u)
    return u


def main() -> None:
    db = SessionLocal()
    svc = LearningService(db)
    try:
        svc._ensure_plan()

        # 1) заявки на преподавателя (pending)
        for email, name, edu, exp in APPLICANTS:
            u = upsert(db, email, name)
            has = db.scalar(
                select(TeacherApplication).where(
                    TeacherApplication.user_id == u.id,
                    TeacherApplication.status == ModerationStatus.pending,
                )
            )
            if has is None:
                db.add(TeacherApplication(
                    user_id=u.id, education=edu, experience=exp,
                    kazakh_level=LanguageLevel.C1, status=ModerationStatus.pending,
                ))
        db.commit()

        teacher = UserRepository(db).get_by_email("teacher@gmail.com")
        u1 = UserRepository(db).get_by_email("user1@gmail.com")
        u2 = UserRepository(db).get_by_email("user2@gmail.com")
        group = db.scalar(select(Group).where(Group.name == "Демо-поток B1"))

        # 2) teacher снова ведёт демо-группу
        if group and teacher:
            group.teacher_id = teacher.id
            db.add(group); db.commit()

        # 3) сданные ДЗ от user1 и user2 — на проверку преподавателю
        if group:
            for student, text in [
                (u1, "Менің диалогым дүкенде: «Сәлеметсіз бе, нан бар ма?»..."),
                (u2, "Үй жұмысым: 5 жаңа сөзбен сөйлем құрадым."),
            ]:
                if student:
                    db.add(Homework(
                        group_id=group.id, student_id=student.id,
                        task="Составьте диалог в магазине (8 реплик) на казахском.",
                        submission=text, status=HomeworkStatus.submitted,
                    ))

            # 4) ДЗ для user1 во всех статусах
            if u1:
                db.add(Homework(group_id=group.id, student_id=u1.id,
                    task="Напишите небольшое эссе «Менің демалысым» (8 предложений).",
                    status=HomeworkStatus.assigned))
                db.add(Homework(group_id=group.id, student_id=u1.id,
                    task="Прочитайте текст и ответьте на вопросы.",
                    submission="Мои ответы на вопросы 1–5...",
                    status=HomeworkStatus.graded, grade=88,
                    feedback="Жақсы! Тек сын есімдерге назар аудар.", graded_by=teacher.id if teacher else None))

            # 5) завершённый урок, который user1 ещё НЕ оценил → отзыв педагогу
            if teacher:
                lesson = Lesson(
                    group_id=group.id, teacher_id=teacher.id,
                    starts_at=datetime.now(timezone.utc) - timedelta(days=1),
                    zoom_link=svc._meeting_link(), status=LessonStatus.completed,
                )
                db.add(lesson); db.flush()
                # на всякий случай убираем оценку user1 для этого урока (её и так нет)
                db.query(LessonRating).filter(
                    LessonRating.lesson_id == lesson.id,
                    LessonRating.student_id == u1.id,
                ).delete()
            db.commit()

        print("✅ Готово.")
        print("   Заявки на преподавателя: applicant1/2/3@gmail.com — в админке → Модерация → Преподаватели")
        print("   teacher@gmail.com ведёт «Демо-поток B1»; есть сданные ДЗ на проверку")
        print("   user1@gmail.com: ДЗ (сдать / на проверке / оценено 88) + завершённый урок для отзыва педагогу")
    finally:
        db.close()


if __name__ == "__main__":
    main()
