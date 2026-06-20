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
    GroupStageProgress,
    Homework,
    Lesson,
    LessonRating,
    Section,
    Stage,
)
from app.db.models.user import User
from app.schemas.learning import (
    ExamResultOut,
    GroupCreateIn,
    GroupOut,
    HomeworkOut,
    LearningOverviewOut,
    LessonOut,
    StageOut,
)

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
        )

    def submit_entrance(self, user: User, answers: dict, listening: dict,
                        reading_text: str | None) -> ExamResultOut:
        if user.role not in (Role.student, Role.teacher):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Сначала станьте учеником")

        choice_score = sum(1 for value in answers.values() if str(value).lower() in {"a", "ә", "1", "true"})
        listening_score = sum(1 for value in listening.values() if len(str(value).strip()) >= 8)
        reading_score = 3 if reading_text and len(reading_text.strip()) >= 40 else 0
        total = min(25, choice_score + listening_score + reading_score)
        percent = round(total / 25 * 100)
        level = self._level_from_score(percent)

        exam = self._ensure_exam()
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
            return [self._lesson_out(lesson) for lesson in lessons]
        group = self._current_group(user)
        if group is None:
            return []
        lessons = self.db.scalars(
            select(Lesson).where(Lesson.group_id == group.id).order_by(Lesson.starts_at.desc())
        ).all()
        return [self._lesson_out(lesson) for lesson in lessons]

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
            zoom_link=self._google_meet_link(),
            status=LessonStatus.scheduled,
        )
        self.db.add(group)
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return self._lesson_out(lesson)

    def submit_level_exam(self, user: User, answers: dict, reading_text: str | None) -> ExamResultOut:
        self._ensure_student_ready(user)
        choice_score = sum(1 for value in answers.values() if str(value).lower() in {"a", "ә", "1", "true"})
        reading_score = 3 if reading_text and len(reading_text.strip()) >= 40 else 0
        total = min(20, choice_score + reading_score)
        percent = round(total / 20 * 100)
        current_index = LEVELS.index(user.level)
        passed = percent >= 70 and current_index < len(LEVELS) - 1
        next_level = LEVELS[current_index + 1] if passed else user.level
        if passed:
            user.level = next_level
            if user.rank in RANKS and RANKS.index(user.rank) < len(RANKS) - 1:
                user.rank = RANKS[RANKS.index(user.rank) + 1]
            self.db.add(user)
        self.db.commit()
        verdict = (
            f"Экзамен сдан: {percent}%. Новый уровень: {next_level.value}."
            if passed
            else f"Экзамен: {percent}%. Для повышения нужно набрать от 70%."
        )
        return ExamResultOut(score=percent, level=next_level, verdict=verdict)

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
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return self._lesson_out(lesson)

    def homeworks(self, user: User) -> list[HomeworkOut]:
        if user.role == Role.teacher:
            rows = self.db.scalars(select(Homework).order_by(Homework.id.desc()).limit(30)).all()
        else:
            rows = self.db.scalars(
                select(Homework).where(Homework.student_id == user.id).order_by(Homework.id.desc())
            ).all()
        return [self._homework_out(row) for row in rows]

    def submit_homework(self, user: User, homework_id: int, submission: str) -> HomeworkOut:
        homework = self.db.get(Homework, homework_id)
        if homework is None or homework.student_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ДЗ не найдено")
        homework.submission = submission.strip()
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

    def _lesson_out(self, lesson: Lesson) -> LessonOut:
        now = datetime.now(lesson.starts_at.tzinfo) if lesson.starts_at.tzinfo else datetime.utcnow()
        if lesson.status == LessonStatus.scheduled and lesson.starts_at - now <= timedelta(hours=6):
            lesson.status = LessonStatus.open
            self.db.add(lesson)
            self.db.commit()
            self.db.refresh(lesson)
        return LessonOut(
            id=lesson.id,
            group_id=lesson.group_id,
            teacher_id=lesson.teacher_id,
            starts_at=lesson.starts_at,
            meet_link=lesson.zoom_link,
            status=lesson.status,
        )

    def _homework_out(self, homework: Homework) -> HomeworkOut:
        return HomeworkOut(
            id=homework.id,
            group_id=homework.group_id,
            student_id=homework.student_id,
            task=homework.task,
            submission=homework.submission,
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

    def _google_meet_link(self) -> str:
        code = "-".join([uuid.uuid4().hex[:3], uuid.uuid4().hex[:4], uuid.uuid4().hex[:3]])
        return f"https://meet.google.com/{code}"
