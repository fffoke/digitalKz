"""Импорт всех моделей, чтобы они зарегистрировались в Base.metadata
(нужно для Alembic autogenerate и create_all)."""
from app.db.base import Base
from app.db.models.content import Exam, ExamAttempt, Material
from app.db.models.duel import Duel
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
from app.db.models.messaging import Conversation, ConversationParticipant, Message
from app.db.models.notification import Notification
from app.db.models.post import Comment, Like, Post, Report, Repost
from app.db.models.tutor import (
    LearningProfile,
    Result,
    Session,
    Task,
    Turn,
)
from app.db.models.user import Follow, TeacherApplication, User, Verification

__all__ = [
    "Base",
    "User",
    "Verification",
    "Follow",
    "TeacherApplication",
    "Post",
    "Like",
    "Repost",
    "Comment",
    "Report",
    "Conversation",
    "ConversationParticipant",
    "Message",
    "Group",
    "GroupMember",
    "Section",
    "Stage",
    "GroupStageProgress",
    "Lesson",
    "LessonRating",
    "Homework",
    "Material",
    "Exam",
    "ExamAttempt",
    "Duel",
    "Notification",
    "LearningProfile",
    "Task",
    "Session",
    "Turn",
    "Result",
]
