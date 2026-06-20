"""Бизнес-логика AI-собеседника.

Связывает: интересы → генерация заданий (LLM) → диалог голосом
(whisper → LLM) → оценка (LLM). Контекст диалога собирается из таблицы Turn.
"""
import os
import shutil
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session as DbSession

from app.db.enums import SessionStatus, TaskDifficulty, TaskStatus, TurnRole
from app.db.models.tutor import LearningProfile, Result, Session, Task, Turn
from app.db.models.user import User
from app.db.repositories.tutor import (
    LearningProfileRepository,
    ResultRepository,
    SessionRepository,
    TaskRepository,
    TurnRepository,
)
from app.schemas.tutor import CustomTaskIn, InterestsIn, InterestsOut
from app.services.llm import get_llm
from app.services.transcription import transcribe_kazakh

VOICE_DIR = "uploads/voice"


class TutorService:
    def __init__(self, db: DbSession) -> None:
        self.db = db
        self.profiles = LearningProfileRepository(db)
        self.tasks = TaskRepository(db)
        self.sessions = SessionRepository(db)
        self.turns = TurnRepository(db)
        self.results = ResultRepository(db)
        self.llm = get_llm()

    # --- онбординг интересов ---

    def get_interests(self, user: User) -> InterestsOut:
        p = self.profiles.get_by_user(user.id)
        if p is None:
            return InterestsOut(onboarded=False)
        return InterestsOut(
            onboarded=p.onboarded,
            motivation=p.motivation,
            interests=p.interests,
            contexts=p.contexts,
        )

    def save_interests(self, user: User, data: InterestsIn) -> InterestsOut:
        p = self.profiles.get_by_user(user.id)
        if p is None:
            p = LearningProfile(user_id=user.id)
        p.motivation = data.motivation
        p.interests = data.interests
        p.contexts = data.contexts
        p.case_text = data.case_text
        p.onboarded = True
        self.profiles.add(p)
        return self.get_interests(user)

    # --- задания ---

    def generate_tasks(self, user: User) -> list[Task]:
        p = self.profiles.get_by_user(user.id)
        if p is None or not p.onboarded:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Сначала пройдите онбординг")

        level = user.level.value if user.level else "A1"
        raw = self.llm.generate_tasks(
            motivation=p.motivation or "",
            interests=p.interests,
            contexts=p.contexts,
            level=level,
            case_text=p.case_text or "",
        )
        tasks = [
            Task(
                user_id=user.id,
                title=str(t.get("title", "Разговорное задание"))[:200],
                scenario=str(t.get("scenario", "")),
                description=(t.get("description") or None) and str(t["description"]),
                context=(t.get("context") or None) and str(t["context"])[:300],
                difficulty=self._safe_difficulty(t.get("difficulty")),
            )
            for t in raw
        ]
        if not tasks:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Не удалось создать задания")
        return self.tasks.add_many(tasks)

    def create_custom_task(self, user: User, data: CustomTaskIn) -> Task:
        description = self._normalize_text(data.description, max_len=1200)
        if len(description) < 10:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Опишите сценарий подробнее",
            )

        title = self._normalize_text(data.title or "", max_len=120)
        if not title:
            title = self._make_custom_title(description)

        scenario = (
            "Ты AI-собеседник для практики казахского языка. "
            "Разыграй с учеником пользовательский сценарий. "
            "Говори в основном на казахском, но если ученик явно не понимает, "
            "коротко помогай по-русски и возвращай диалог к казахскому. "
            "Не решай задачу за ученика: задавай уточняющие вопросы, поддерживай "
            "естественный разговор и доведи сцену до понятного результата.\n\n"
            f"Сценарий ученика: {description}"
        )

        return self.tasks.add(Task(
            user_id=user.id,
            title=title[:200],
            scenario=scenario,
            description=description,
            context="Свой сценарий",
            difficulty=data.difficulty,
        ))

    def list_tasks(self, user: User) -> list[Task]:
        return self.tasks.list_for_user(user.id)

    def get_task(self, user: User, task_id: int) -> Task:
        task = self.tasks.get(task_id)
        if task is None or task.user_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Задание не найдено")
        return task

    def delete_task(self, user: User, task_id: int) -> None:
        task = self.get_task(user, task_id)
        # удаляем зависимые сессии/реплики/результаты (нет каскада на уровне БД)
        for s in self.sessions.list_for_task(task.id):
            for t in self.turns.list_for_session(s.id):
                self.turns.delete(t)
            r = self.results.get_by_session(s.id)
            if r is not None:
                self.results.delete(r)
            self.sessions.delete(s)
        self.tasks.delete(task)

    # --- сессия диалога ---

    def start_task(self, user: User, task_id: int) -> tuple[Session, str]:
        task = self.get_task(user, task_id)

        # возобновляем незавершённую сессию — иначе история диалога теряется
        existing = self.sessions.get_active_for_task(user.id, task.id)
        if existing is not None:
            turns = self.turns.list_for_session(existing.id)
            last_ai = next(
                (t.text for t in reversed(turns) if t.role == TurnRole.ai), ""
            )
            return existing, last_ai or ""

        session = self.sessions.add(
            Session(task_id=task.id, user_id=user.id, status=SessionStatus.active)
        )
        if task.status == TaskStatus.new:
            task.status = TaskStatus.in_progress
            self.tasks.add(task)

        # первое сообщение ИИ (история пустая → приветствие по сценарию)
        ai_text = self.llm.reply(scenario=task.scenario, history=[])
        self.turns.add(Turn(session_id=session.id, role=TurnRole.ai, text=ai_text))
        return session, ai_text

    def get_session(self, user: User, session_id: int) -> Session:
        s = self.sessions.get(session_id)
        if s is None or s.user_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Сессия не найдена")
        return s

    def list_turns(self, session_id: int) -> list[Turn]:
        return self.turns.list_for_session(session_id)

    def get_result(self, session_id: int) -> Result | None:
        return self.results.get_by_session(session_id)

    def send_message(self, user: User, session_id: int, audio: UploadFile,
                     base_url: str = "") -> dict:
        session = self.get_session(user, session_id)
        if session.status != SessionStatus.active:
            raise HTTPException(status.HTTP_409_CONFLICT, "Сессия уже завершена")
        task = self.tasks.get(session.task_id)

        # 1. сохраняем аудио и расшифровываем
        path, url = self._save_audio(audio, base_url)
        transcript = transcribe_kazakh(path)

        # 2. сохраняем реплику ученика
        user_turn = self.turns.add(Turn(
            session_id=session.id, role=TurnRole.user,
            transcript=transcript, audio_url=url,
        ))

        # 3. если речь не распозналась — не зовём ИИ (иначе он повторяет приветствие),
        #    а просим повторить
        if not transcript.strip():
            ai_text = "Кешіріңіз, дауысыңызды танымадым. Қайталап айтып көріңізші 🙏"
        else:
            history = self._history(session.id)
            ai_text = self.llm.reply(scenario=task.scenario, history=history)

        self.turns.add(Turn(session_id=session.id, role=TurnRole.ai, text=ai_text))
        return {"transcript": transcript, "ai_text": ai_text, "turn": user_turn}

    def finish_session(self, user: User, session_id: int) -> Result:
        session = self.get_session(user, session_id)
        existing = self.results.get_by_session(session.id)
        if existing is not None:
            return existing

        task = self.tasks.get(session.task_id)
        history = self._history(session.id)
        verdict = self.llm.evaluate(
            scenario=task.scenario, title=task.title, history=history,
        )

        result = self.results.add(Result(
            session_id=session.id,
            task_score=verdict["task_score"],
            language_score=verdict["language_score"],
            feedback=verdict.get("feedback"),
        ))

        # закрываем сессию и помечаем задание пройденным
        session.status = SessionStatus.finished
        session.finished_at = datetime.now(timezone.utc)
        self.sessions.add(session)

        task.status = TaskStatus.done
        task.score = verdict["task_score"]
        task.speaking_score = verdict["language_score"]
        self.tasks.add(task)
        return result

    # --- статистика ученика (подвкладка в профиле) ---

    def stats(self, user: User) -> dict:
        tasks = self.tasks.list_for_user(user.id)
        done = [t for t in tasks if t.status == TaskStatus.done]
        speaking = [t.speaking_score for t in done if t.speaking_score is not None]
        task_scores = [t.score for t in done if t.score is not None]

        def avg(xs: list[int]) -> int:
            return round(sum(xs) / len(xs)) if xs else 0

        by_diff = []
        for diff in (TaskDifficulty.easy, TaskDifficulty.medium, TaskDifficulty.hard):
            d = [t for t in done if t.difficulty == diff]
            ss = [t.speaking_score for t in d if t.speaking_score is not None]
            by_diff.append({
                "difficulty": diff,
                "done": len(d),
                "avg_speaking": avg(ss),
            })

        return {
            "total": len(tasks),
            "done": len(done),
            "avg_speaking": avg(speaking),
            "best_speaking": max(speaking) if speaking else 0,
            "avg_task": avg(task_scores),
            "by_difficulty": by_diff,
        }

    # --- вспомогательное ---

    def _history(self, session_id: int) -> list[dict]:
        """Реплики из БД → формат чата для LLM."""
        out = []
        for t in self.turns.list_for_session(session_id):
            if t.role == TurnRole.user and t.transcript:
                out.append({"role": "user", "content": t.transcript})
            elif t.role == TurnRole.ai and t.text:
                out.append({"role": "assistant", "content": t.text})
        return out

    def _normalize_text(self, value: str, *, max_len: int) -> str:
        return " ".join((value or "").strip().split())[:max_len]

    def _make_custom_title(self, description: str) -> str:
        first_sentence = description.split(".")[0].strip()
        if first_sentence:
            return first_sentence[:80]
        return "Свой сценарий"

    def _save_audio(self, audio: UploadFile, base_url: str = "") -> tuple[str, str]:
        os.makedirs(VOICE_DIR, exist_ok=True)
        ext = os.path.splitext(audio.filename or "")[1].lower() or ".webm"
        name = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(VOICE_DIR, name)
        with open(path, "wb") as f:
            shutil.copyfileobj(audio.file, f)
        base = base_url.rstrip("/")
        return path, f"{base}/uploads/voice/{name}"

    @staticmethod
    def _safe_difficulty(value) -> str:
        try:
            return TaskDifficulty(value)
        except (ValueError, TypeError):
            return TaskDifficulty.medium
