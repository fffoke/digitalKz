"""Демо: группы без преподавателя + живые чаты.

Запуск (в контейнере backend):
    python -m app.scripts.seed_chats

- Создаёт несколько групп БЕЗ преподавателя (попадают в «Группы без преподавателя»).
- Очищает все сообщения групп и наполняет чаты живым общением на казахском.
"""
import uuid

from sqlalchemy import select

from app.core.security import hash_password
from app.db.enums import LanguageLevel, Rank, Role, Schedule
from app.db.models.learning import Group, GroupMember, GroupMessage
from app.db.models.user import User
from app.db.repositories.user import UserRepository
from app.db.session import SessionLocal
from app.services.learning import LearningService

PASSWORD = "password123"

EXTRA_STUDENTS = [
    ("dana@gmail.com", "Дана"),
    ("aru@gmail.com", "Аружан Қ."),
    ("bek@gmail.com", "Бекжан"),
    ("nur@gmail.com", "Нұрсұлтан"),
    ("mira@gmail.com", "Мира"),
]

# (название, уровень, индексы участников из all_students)
NO_TEACHER_GROUPS = [
    ("Сөйлеу клубы B1", LanguageLevel.B1, [0, 1, 2]),
    ("Кешкі топ B1", LanguageLevel.B1, [2, 3, 4]),
    ("Жаңадан бастаушылар A2", LanguageLevel.A2, [3, 4]),
]

# живой диалог: (индекс участника группы, текст)
CONVERSATION = [
    (0, "Сәлеметсіздер ме, бәрі дайын ба бүгінгі сабаққа? 😊"),
    (1, "Сәлем! Иә, мен дайынмын, үй жұмысын да істедім 💪"),
    (2, "Мен сәл кешігемін, кофе ішіп жатырмын ☕️"),
    (0, "Кеше жаңа сөздерді жаттадым: «тапсырыс», «есеп», «мәзір» 📖"),
    (1, "Жарайсың! Маған «мәзір» сөзі ұнайды 😄"),
    (2, "Мұғалім бүгін кафедегі диалогты тапсырма ретінде берді ме?"),
    (0, "Иә! Бірге жаттығайық па? Кім бариста болады? 🎤"),
    (1, "Мен болам! «Сізге қандай кофе керек?» 😁"),
    (2, "Маған капучино, рахмет! ☕️"),
    (0, "Керемет шықты! Сабақтан кейін тағы практика жасайық 🔥"),
    (1, "Келісемін. Сәттілік бәрімізге! 🙌"),
]


def get_or_create_student(db, email, name) -> User:
    user = UserRepository(db).get_by_email(email)
    if user is None:
        user = User(name=name, email=email, password_hash=hash_password(PASSWORD))
        db.add(user)
    user.name = name
    user.password_hash = hash_password(PASSWORD)
    user.role = Role.student
    user.level = LanguageLevel.B1
    user.rank = Rank.orta
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def fill_chat(db, group: Group, members: list[User]) -> None:
    for idx, text in CONVERSATION:
        sender = members[idx % len(members)]
        db.add(GroupMessage(group_id=group.id, sender_id=sender.id, text=text))
    db.commit()


def main() -> None:
    db = SessionLocal()
    svc = LearningService(db)
    try:
        svc._ensure_plan()

        students = [get_or_create_student(db, e, n) for e, n in EXTRA_STUDENTS]
        # подмешаем демо-учеников, если есть
        for em in ("user1@gmail.com", "user2@gmail.com"):
            u = UserRepository(db).get_by_email(em)
            if u:
                students.insert(0, u)

        # очищаем ВСЕ сообщения групп
        db.query(GroupMessage).delete()
        db.commit()
        print("🧹 Все чаты очищены.")

        # группы без преподавателя
        created = []
        for name, level, idxs in NO_TEACHER_GROUPS:
            group = db.scalar(select(Group).where(Group.name == name))
            members = [students[i % len(students)] for i in idxs]
            if group is None:
                group = Group(
                    name=name, level=level, schedule=Schedule.three_week,
                    invite_code=uuid.uuid4().hex[:10], teacher_id=None,
                    current_section=1, current_stage=1,
                )
                db.add(group)
                db.flush()
                svc._init_group_progress(group)
            group.teacher_id = None  # без преподавателя
            for m in members:
                if db.get(GroupMember, {"group_id": group.id, "user_id": m.id}) is None:
                    db.add(GroupMember(group_id=group.id, user_id=m.id))
            db.commit()
            created.append((group, members))

        # наполняем чаты живым общением (включая демо-группу, если есть)
        demo = db.scalar(select(Group).where(Group.name == "Демо-поток B1"))
        if demo:
            demo_members = [
                db.get(User, gm.user_id)
                for gm in db.scalars(select(GroupMember).where(GroupMember.group_id == demo.id)).all()
            ]
            if demo_members:
                fill_chat(db, demo, demo_members)
        for group, members in created:
            fill_chat(db, group, members)

        print(f"✅ Создано групп без преподавателя: {len(created)}")
        for g, _ in created:
            print(f"   - {g.name} ({g.level.value})")
        print("💬 Чаты наполнены живым общением на казахском.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
