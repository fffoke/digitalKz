"""Основная логика вкладки «Обучение»: тест, группы, уроки, ДЗ."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.db.enums import (
    HomeworkStatus,
    ExamType,
    LanguageLevel,
    LessonStatus,
    Rank,
    Role,
    Schedule,
    StageStatus,
)
from app.db.models.content import Exam, ExamAttempt
from app.db.models.learning import (
    Group,
    GroupMember,
    GroupMessage,
    GroupStageProgress,
    Homework,
    Lesson,
    LessonRating,
    Section,
    Stage,
)
from app.db.models.user import User
from app.schemas.learning import (
    EntranceExamOut,
    EntranceQuestionOut,
    ExamResultOut,
    GroupCreateIn,
    GroupMessageOut,
    GroupOut,
    HomeworkOut,
    LearningOverviewOut,
    LessonOut,
    LevelExamOut,
    LevelExamQuestionOut,
    StageOut,
)
from app.services.transcription import transcribe_kazakh

EXAM_COOLDOWN_DAYS = 14  # досрочно экзамен можно сдавать раз в 2 недели

LEVELS = [LanguageLevel.A1, LanguageLevel.A2, LanguageLevel.B1, LanguageLevel.B2, LanguageLevel.C1]
RANKS = [Rank.bastauysh, Rank.orta, Rank.jetik, Rank.sheber, Rank.ustaz]


class LearningService:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def overview(self, user: User) -> LearningOverviewOut:
        self._ensure_plan()
        current_group = self._current_group(user)
        return LearningOverviewOut(
            role=user.role,
            level=user.level,
            rank=user.rank,
            needs_entrance_test=user.role == Role.student and user.level is None,
            current_group=self._group_out(current_group, user) if current_group else None,
            available_groups=self.available_groups(user),
            progress=self.progress(user),
            lessons=self.lessons(user),
            homeworks=self.homeworks(user),
            open_teacher_groups=self.open_teacher_groups(user) if user.role == Role.teacher else [],
            teacher_groups=self.teacher_groups(user) if user.role == Role.teacher else [],
        )

    def teacher_groups(self, user: User) -> list[GroupOut]:
        if user.role != Role.teacher:
            return []
        groups = self.db.scalars(
            select(Group).where(Group.teacher_id == user.id).order_by(Group.id.desc())
        ).all()
        return [self._group_out(group, user) for group in groups]

    def entrance_exam(self, user: User) -> EntranceExamOut:
        """Вопросы вступительного теста для ученика — без правильных ответов."""
        exam = self._ensure_exam()
        questions = [
            EntranceQuestionOut(
                type=q.get("type", "choice"),
                text=q.get("text", ""),
                options=q.get("options", []),
            )
            for q in (exam.questions or [])
        ]
        return EntranceExamOut(questions=questions, voice_task=exam.voice_task)

    def submit_entrance(self, user: User, answers: dict, listening: dict,
                        reading_text: str | None) -> ExamResultOut:
        if user.role not in (Role.student, Role.teacher):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Сначала станьте учеником")

        exam = self._ensure_exam()
        questions = exam.questions or []

        # сверяем ответы ученика с правильными (вопросы заданы в админке)
        choice_qs = [(i, q) for i, q in enumerate(questions) if q.get("type") == "choice"]
        correct = sum(
            1 for i, q in choice_qs
            if q.get("answer")
            and str(answers.get(f"q{i}", "")).strip().lower()
            == str(q.get("answer", "")).strip().lower()
        )
        choice_pct = correct / len(choice_qs) if choice_qs else 0
        listening_ok = sum(1 for value in listening.values() if len(str(value).strip()) >= 8)
        reading_ok = 1 if reading_text and len(reading_text.strip()) >= 40 else 0
        # вес: варианты 70%, аудирование 20%, чтение 10%
        percent = round(choice_pct * 70 + min(1, listening_ok / 3) * 20 + reading_ok * 10)
        level = self._level_from_score(percent)

        attempt = ExamAttempt(
            exam_id=exam.id,
            user_id=user.id,
            answers={"answers": answers, "listening": listening},
            transcript=reading_text,
            verdict=f"Вступительный тест: {percent}%. Уровень: {level.value}.",
            result_level=level,
            score=percent,
        )
        self.db.add(attempt)
        user.level = level
        user.rank = user.rank or Rank.bastauysh
        self.db.add(user)
        self.db.commit()
        return ExamResultOut(score=percent, level=level, verdict=attempt.verdict)

    def available_groups(self, user: User) -> list[GroupOut]:
        if user.role not in (Role.student, Role.teacher) or user.level is None:
            return []
        groups = self.db.scalars(select(Group).order_by(Group.id.desc())).all()
        return [
            self._group_out(group, user)
            for group in groups
            if self._same_level_band(user.level, group.level)
            and self._members_count(group.id) < 5
            and not self._is_member(group.id, user.id)
        ]

    def create_group(self, user: User, data: GroupCreateIn) -> GroupOut:
        self._ensure_plan()
        self._ensure_student_ready(user)
        group = Group(
            name=(data.name or f"Поток {user.level.value}")[:120],
            level=user.level,
            schedule=data.schedule,
            invite_code=uuid.uuid4().hex[:10],
            current_section=1,
            current_stage=1,
        )
        self.db.add(group)
        self.db.flush()
        self.db.add(GroupMember(group_id=group.id, user_id=user.id))
        self._init_group_progress(group)
        self.db.commit()
        self.db.refresh(group)
        return self._group_out(group, user)

    def join_group(self, user: User, group_id: int) -> GroupOut:
        self._ensure_student_ready(user)
        group = self._get_group(group_id)
        if not self._same_level_band(user.level, group.level):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Группа не подходит по уровню")
        if self._members_count(group.id) >= 5:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Группа уже заполнена")
        if not self._is_member(group.id, user.id):
            self.db.add(GroupMember(group_id=group.id, user_id=user.id))
            self.db.commit()
        return self._group_out(group, user)

    def join_by_code(self, user: User, invite_code: str) -> GroupOut:
        group = self.db.scalar(select(Group).where(Group.invite_code == invite_code.strip()))
        if group is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Группа не найдена")
        return self.join_group(user, group.id)

    def leave_group(self, user: User, group_id: int) -> None:
        member = self.db.get(GroupMember, {"group_id": group_id, "user_id": user.id})
        if member is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Вы не состоите в группе")
        self.db.delete(member)
        self.db.commit()

    # --- чат группы ---

    def _ensure_group_access(self, user: User, group_id: int) -> Group:
        group = self._get_group(group_id)
        if not self._is_member(group_id, user.id) and group.teacher_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Вы не состоите в этой группе")
        return group

    def group_messages(self, user: User, group_id: int) -> list[GroupMessageOut]:
        self._ensure_group_access(user, group_id)
        rows = self.db.execute(
            select(GroupMessage, User)
            .join(User, User.id == GroupMessage.sender_id)
            .where(GroupMessage.group_id == group_id)
            .order_by(GroupMessage.id)
        ).all()
        return [
            GroupMessageOut(
                id=m.id, sender_id=m.sender_id, sender_name=u.name,
                sender_avatar=u.avatar,
                text=m.text, created_at=m.created_at, is_mine=m.sender_id == user.id,
            )
            for m, u in rows
        ]

    def post_group_message(self, user: User, group_id: int, text: str) -> GroupMessageOut:
        self._ensure_group_access(user, group_id)
        text = (text or "").strip()
        if not text:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Пустое сообщение")
        msg = GroupMessage(group_id=group_id, sender_id=user.id, text=text[:2000])
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return GroupMessageOut(
            id=msg.id, sender_id=user.id, sender_name=user.name,
            sender_avatar=user.avatar,
            text=msg.text, created_at=msg.created_at, is_mine=True,
        )

    def progress(self, user: User) -> list[StageOut]:
        group = self._current_group(user)
        if group is None:
            return []
        stages = self.db.execute(
            select(Section, Stage, GroupStageProgress)
            .join(Stage, Stage.section_id == Section.id)
            .join(GroupStageProgress, GroupStageProgress.stage_id == Stage.id)
            .where(GroupStageProgress.group_id == group.id)
            .order_by(Section.order, Stage.order)
        ).all()
        return [
            StageOut(section=section.order, stage=stage.order, title=stage.title, status=progress.status)
            for section, stage, progress in stages
        ]

    def lessons(self, user: User) -> list[LessonOut]:
        if user.role == Role.teacher:
            lessons = self.db.scalars(
                select(Lesson).where(Lesson.teacher_id == user.id).order_by(Lesson.starts_at.desc())
            ).all()
            return [self._lesson_out(lesson, user) for lesson in lessons]
        group = self._current_group(user)
        if group is None:
            return []
        lessons = self.db.scalars(
            select(Lesson).where(Lesson.group_id == group.id).order_by(Lesson.starts_at.desc())
        ).all()
        return [self._lesson_out(lesson, user) for lesson in lessons]

    def open_teacher_groups(self, user: User) -> list[GroupOut]:
        if user.role != Role.teacher:
            return []
        groups = self.db.scalars(
            select(Group).where(Group.teacher_id.is_(None)).order_by(Group.id.desc())
        ).all()
        return [self._group_out(group, user) for group in groups if self._members_count(group.id) >= 2]

    def schedule_lesson(self, user: User, group_id: int, starts_at: datetime) -> LessonOut:
        if user.role != Role.teacher:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Только для преподавателей")
        group = self._get_group(group_id)
        if group.teacher_id not in (None, user.id):
            raise HTTPException(status.HTTP_409_CONFLICT, "Группу уже взял другой преподаватель")
        group.teacher_id = user.id
        lesson = Lesson(
            group_id=group.id,
            teacher_id=user.id,
            starts_at=starts_at,
            zoom_link=self._meeting_link(),
            status=LessonStatus.scheduled,
        )
        self.db.add(group)
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return self._lesson_out(lesson)

    def start_lesson(self, user: User, group_id: int) -> LessonOut:
        """Мгновенный урок: создаём видеокомнату и кидаем ссылку в чат группы."""
        if user.role != Role.teacher:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Только для преподавателей")
        group = self._get_group(group_id)
        if group.teacher_id not in (None, user.id):
            raise HTTPException(status.HTTP_409_CONFLICT, "Группу уже взял другой преподаватель")
        group.teacher_id = user.id
        meet = self._meeting_link()
        lesson = Lesson(
            group_id=group.id, teacher_id=user.id,
            starts_at=datetime.now(timezone.utc),
            zoom_link=meet, status=LessonStatus.open,
        )
        self.db.add(group)
        self.db.add(lesson)
        self.db.add(GroupMessage(
            group_id=group.id, sender_id=user.id,
            text=f"📹 Урок начался! Подключайтесь к видеоуроку: {meet}",
        ))
        self.db.commit()
        self.db.refresh(lesson)
        return self._lesson_out(lesson)

    # --- экзамен на повышение уровня ---

    def _next_level(self, user: User):
        idx = LEVELS.index(user.level)
        return LEVELS[idx + 1] if idx < len(LEVELS) - 1 else None

    def _level_exam_record(self, target_level):
        if target_level is None:
            return None
        return self.db.scalar(
            select(Exam)
            .where(Exam.type == ExamType.level, Exam.target_level == target_level)
            .order_by(Exam.id.desc())
        )

    def _ensure_level_exam(self, target_level) -> Exam:
        """Гарантирует запись экзамена на уровень (пустую, если админ не создал) —
        чтобы попытки привязывались к type=level и работал лимит раз в 2 недели."""
        exam = self._level_exam_record(target_level)
        if exam is None:
            exam = Exam(
                title=f"Экзамен на {target_level.value}",
                type=ExamType.level,
                target_level=target_level,
                questions=[],
                voice_task="Прочитайте короткий текст на казахском вслух.",
            )
            self.db.add(exam)
            self.db.commit()
            self.db.refresh(exam)
        return exam

    def _last_level_attempt(self, user: User):
        return self.db.scalar(
            select(ExamAttempt)
            .join(Exam, Exam.id == ExamAttempt.exam_id)
            .where(ExamAttempt.user_id == user.id, Exam.type == ExamType.level)
            .order_by(ExamAttempt.id.desc())
        )

    def _cooldown(self, user: User):
        """→ (can_take, next_available_at). Досрочно — раз в 2 недели."""
        last = self._last_level_attempt(user)
        if last is None:
            return True, None
        created = last.created_at
        nxt = created + timedelta(days=EXAM_COOLDOWN_DAYS)
        now = datetime.now(created.tzinfo) if created.tzinfo else datetime.utcnow()
        return now >= nxt, (None if now >= nxt else nxt)

    def level_exam(self, user: User) -> LevelExamOut:
        self._ensure_student_ready(user)
        target = self._next_level(user)
        exam = self._level_exam_record(target)
        can_take, nxt = self._cooldown(user)
        questions = [
            LevelExamQuestionOut(
                type=q.get("type", "choice"), text=q.get("text", ""),
                options=q.get("options", []), audio_url=q.get("audio_url"),
            )
            for q in (exam.questions if exam else [])
        ]
        return LevelExamOut(
            target_level=target,
            voice_task=exam.voice_task if exam else "Прочитайте короткий текст на казахском вслух.",
            questions=questions,
            can_take=can_take,
            next_available_at=nxt,
            configured=bool(exam and exam.questions),
        )

    def submit_level_exam(self, user: User, answers: dict, audio_path: str | None) -> ExamResultOut:
        self._ensure_student_ready(user)
        can_take, nxt = self._cooldown(user)
        if not can_take:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Досрочно экзамен можно сдавать раз в 2 недели. Следующая попытка: "
                f"{nxt.strftime('%d.%m.%Y') if nxt else 'позже'}.",
            )

        target = self._next_level(user)
        if target is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Вы достигли максимального уровня (C1)")
        exam = self._ensure_level_exam(target)   # привязка попытки к type=level
        questions = exam.questions or []

        graded = [(i, q) for i, q in enumerate(questions) if q.get("type") in ("choice", "listening")]
        correct = sum(
            1 for i, q in graded
            if q.get("answer")
            and str(answers.get(f"q{i}", "")).strip().lower() == str(q.get("answer")).strip().lower()
        )
        knowledge_pct = correct / len(graded) if graded else 0

        # говорение: реальная запись → распознавание
        transcript = transcribe_kazakh(audio_path) if audio_path else ""
        words = len(transcript.split())
        speaking = 1.0 if words >= 6 else (0.5 if transcript.strip() else 0.0)

        # вес: знания 70%, говорение 30%. Если вопросов нет — экзамен по говорению.
        percent = round((knowledge_pct * 70 + speaking * 30) if graded else speaking * 100)

        current_index = LEVELS.index(user.level)
        passed = percent >= 70 and current_index < len(LEVELS) - 1
        next_level = LEVELS[current_index + 1] if passed else user.level

        attempt = ExamAttempt(
            exam_id=exam.id,
            user_id=user.id,
            answers={"answers": answers},
            transcript=transcript or None,
            verdict="",
            result_level=next_level,
            score=percent,
        )
        if passed:
            user.level = next_level
            if user.rank in RANKS and RANKS.index(user.rank) < len(RANKS) - 1:
                user.rank = RANKS[RANKS.index(user.rank) + 1]
            self.db.add(user)
        attempt.verdict = (
            f"Экзамен сдан: {percent}%. Новый уровень: {next_level.value}."
            if passed
            else f"Экзамен: {percent}%. Для повышения нужно набрать от 70%."
        )
        self.db.add(attempt)
        self.db.commit()
        return ExamResultOut(score=percent, level=next_level, verdict=attempt.verdict)

    def complete_lesson(self, user: User, lesson_id: int) -> LessonOut:
        lesson = self._get_lesson(lesson_id)
        if lesson.teacher_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Это урок другого преподавателя")
        lesson.status = LessonStatus.completed
        group = self._get_group(lesson.group_id)
        for member in self.db.scalars(select(GroupMember).where(GroupMember.group_id == group.id)).all():
            exists = self.db.scalar(
                select(Homework).where(
                    Homework.group_id == group.id,
                    Homework.student_id == member.user_id,
                    Homework.status == HomeworkStatus.assigned,
                )
            )
            if exists is None:
                self.db.add(Homework(
                    group_id=group.id,
                    student_id=member.user_id,
                    task=f"Повторите секцию {group.current_section}, этап {group.current_stage}: составьте 5 фраз и короткий диалог.",
                    status=HomeworkStatus.assigned,
                ))
        self._advance_group(group)
        # урок проведён → освобождаем группу: она возвращается в общий пул,
        # следующий урок (и проверку ДЗ) берёт следующий преподаватель
        group.teacher_id = None
        self.db.add(group)
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return self._lesson_out(lesson)

    def homeworks(self, user: User) -> list[HomeworkOut]:
        if user.role == Role.teacher:
            # ДЗ из групп, которые ведёт преподаватель; отправленные на проверку — выше
            rows = self.db.scalars(
                select(Homework)
                .join(Group, Group.id == Homework.group_id)
                .where(Group.teacher_id == user.id)
                .order_by(Homework.id.desc())
            ).all()
            order = {HomeworkStatus.submitted: 0, HomeworkStatus.assigned: 1, HomeworkStatus.graded: 2}
            rows = sorted(rows, key=lambda h: order.get(h.status, 3))
        else:
            rows = self.db.scalars(
                select(Homework).where(Homework.student_id == user.id).order_by(Homework.id.desc())
            ).all()
        return [self._homework_out(row) for row in rows]

    def submit_homework(self, user: User, homework_id: int, submission: str,
                        file_url: str | None = None) -> HomeworkOut:
        homework = self.db.get(Homework, homework_id)
        if homework is None or homework.student_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ДЗ не найдено")
        if not (submission or "").strip() and not file_url:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Добавьте текст или файл")
        homework.submission = (submission or "").strip() or None
        if file_url:
            homework.submission_file = file_url
        homework.status = HomeworkStatus.submitted
        self.db.add(homework)
        self.db.commit()
        self.db.refresh(homework)
        return self._homework_out(homework)

    def grade_homework(self, user: User, homework_id: int, grade: int,
                       feedback: str | None) -> HomeworkOut:
        if user.role != Role.teacher:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Только для преподавателей")
        if grade < 1 or grade > 100:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Оценка должна быть от 1 до 100")
        homework = self.db.get(Homework, homework_id)
        if homework is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ДЗ не найдено")
        homework.grade = grade
        homework.feedback = feedback
        homework.graded_by = user.id
        homework.status = HomeworkStatus.graded
        self.db.add(homework)
        self.db.commit()
        self.db.refresh(homework)
        return self._homework_out(homework)

    def rate_lesson(self, user: User, lesson_id: int, score: int,
                    review: str | None, anonymous: bool) -> None:
        if score < 1 or score > 5:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Оценка должна быть от 1 до 5")
        lesson = self._get_lesson(lesson_id)
        if not self._is_member(lesson.group_id, user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Вы не участник группы")
        existing = self.db.scalar(
            select(LessonRating).where(
                LessonRating.lesson_id == lesson.id,
                LessonRating.student_id == user.id,
            )
        )
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Вы уже оценили этот урок")
        self.db.add(LessonRating(
            lesson_id=lesson.id,
            student_id=user.id,
            score=score,
            review=review,
            anonymous=anonymous,
        ))
        self.db.commit()

    def _ensure_student_ready(self, user: User) -> None:
        if user.role not in (Role.student, Role.teacher):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Сначала станьте учеником")
        if user.level is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Сначала пройдите вступительный тест")

    def _current_group(self, user: User) -> Group | None:
        member = self.db.scalar(select(GroupMember).where(GroupMember.user_id == user.id))
        return self.db.get(Group, member.group_id) if member else None

    def _get_group(self, group_id: int) -> Group:
        group = self.db.get(Group, group_id)
        if group is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Группа не найдена")
        return group

    def _get_lesson(self, lesson_id: int) -> Lesson:
        lesson = self.db.get(Lesson, lesson_id)
        if lesson is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Урок не найден")
        return lesson

    def _members_count(self, group_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id)
        ) or 0

    def _is_member(self, group_id: int, user_id: int) -> bool:
        return self.db.get(GroupMember, {"group_id": group_id, "user_id": user_id}) is not None

    def _same_level_band(self, user_level: LanguageLevel, group_level: LanguageLevel) -> bool:
        return abs(LEVELS.index(user_level) - LEVELS.index(group_level)) <= 1

    def _group_out(self, group: Group, user: User) -> GroupOut:
        return GroupOut(
            id=group.id,
            name=group.name,
            level=group.level,
            schedule=group.schedule,
            invite_code=group.invite_code,
            teacher_id=group.teacher_id,
            current_section=group.current_section,
            current_stage=group.current_stage,
            members_count=self._members_count(group.id),
            is_member=self._is_member(group.id, user.id),
        )

    def _lesson_out(self, lesson: Lesson, user: User | None = None) -> LessonOut:
        now = datetime.now(lesson.starts_at.tzinfo) if lesson.starts_at.tzinfo else datetime.utcnow()
        ends = lesson.starts_at + timedelta(hours=1)
        # урок прошёл → авто-завершение (скрыть «Подключиться», открыть оценку)
        if lesson.status in (LessonStatus.scheduled, LessonStatus.open) and now >= ends:
            lesson.status = LessonStatus.completed
            self.db.add(lesson); self.db.commit(); self.db.refresh(lesson)
        # за 6ч до начала → открыт
        elif lesson.status == LessonStatus.scheduled and lesson.starts_at - now <= timedelta(hours=6):
            lesson.status = LessonStatus.open
            self.db.add(lesson); self.db.commit(); self.db.refresh(lesson)

        teacher = self.db.get(User, lesson.teacher_id)
        rated, my_score, my_review = False, None, None
        if user is not None:
            r = self.db.scalar(
                select(LessonRating).where(
                    LessonRating.lesson_id == lesson.id,
                    LessonRating.student_id == user.id,
                )
            )
            if r is not None:
                rated, my_score, my_review = True, r.score, r.review
        return LessonOut(
            id=lesson.id,
            group_id=lesson.group_id,
            teacher_id=lesson.teacher_id,
            teacher_name=teacher.name if teacher else None,
            starts_at=lesson.starts_at,
            ends_at=ends,
            meet_link=lesson.zoom_link,
            status=lesson.status,
            rated=rated, my_score=my_score, my_review=my_review,
        )

    def _homework_out(self, homework: Homework) -> HomeworkOut:
        student = self.db.get(User, homework.student_id)
        group = self.db.get(Group, homework.group_id)
        return HomeworkOut(
            id=homework.id,
            group_id=homework.group_id,
            group_name=group.name if group else None,
            student_id=homework.student_id,
            student_name=student.name if student else None,
            task=homework.task,
            submission=homework.submission,
            submission_file=homework.submission_file,
            status=homework.status,
            grade=homework.grade,
            feedback=homework.feedback,
        )

    def _ensure_plan(self) -> None:
        if self.db.scalar(select(func.count()).select_from(Section)):
            return
        for level in LEVELS:
            for section_no in range(1, 4):
                section = Section(
                    level=level,
                    order=section_no,
                    title=f"{level.value}: секция {section_no}",
                )
                self.db.add(section)
                self.db.flush()
                for stage_no in range(1, 4):
                    self.db.add(Stage(
                        section_id=section.id,
                        order=stage_no,
                        title=f"Этап {stage_no}: разговорная практика",
                    ))
        self.db.commit()

    def _init_group_progress(self, group: Group) -> None:
        stages = self.db.execute(
            select(Section, Stage)
            .join(Stage, Stage.section_id == Section.id)
            .where(Section.level == group.level)
            .order_by(Section.order, Stage.order)
        ).all()
        for section, stage in stages:
            status_ = StageStatus.current if section.order == 1 and stage.order == 1 else StageStatus.locked
            self.db.add(GroupStageProgress(group_id=group.id, stage_id=stage.id, status=status_))

    def _advance_group(self, group: Group) -> None:
        current = self.db.scalar(
            select(GroupStageProgress)
            .join(Stage, Stage.id == GroupStageProgress.stage_id)
            .join(Section, Section.id == Stage.section_id)
            .where(
                GroupStageProgress.group_id == group.id,
                Section.order == group.current_section,
                Stage.order == group.current_stage,
            )
        )
        if current:
            current.status = StageStatus.done

        group.current_stage += 1
        if group.current_stage > 3:
            group.current_stage = 1
            group.current_section = min(group.current_section + 1, 3)

        next_progress = self.db.scalar(
            select(GroupStageProgress)
            .join(Stage, Stage.id == GroupStageProgress.stage_id)
            .join(Section, Section.id == Stage.section_id)
            .where(
                GroupStageProgress.group_id == group.id,
                Section.order == group.current_section,
                Stage.order == group.current_stage,
            )
        )
        if next_progress and next_progress.status != StageStatus.done:
            next_progress.status = StageStatus.current
        self.db.add(group)

    def _ensure_exam(self) -> Exam:
        exam = self.db.scalar(select(Exam).where(Exam.title == "Вступительный тест"))
        if exam:
            return exam
        exam = Exam(
            title="Вступительный тест",
            type=ExamType.entrance,
            target_level=None,
            questions=[{"type": "choice", "text": f"Вопрос {i}", "answer": "a"} for i in range(1, 26)],
            voice_task="Прочитайте короткий текст на казахском.",
        )
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def _level_from_score(self, score: int) -> LanguageLevel:
        if score >= 85:
            return LanguageLevel.C1
        if score >= 70:
            return LanguageLevel.B2
        if score >= 50:
            return LanguageLevel.B1
        if score >= 30:
            return LanguageLevel.A2
        return LanguageLevel.A1

    def _meeting_link(self) -> str:
        """Ссылка на видеокомнату Jitsi — реальная общая комната, без API и логина."""
        from app.core.config import settings
        room = "tildes-" + uuid.uuid4().hex[:18]
        return f"{settings.JITSI_BASE_URL.rstrip('/')}/{room}"
