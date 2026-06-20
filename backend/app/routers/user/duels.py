"""Эндпоинты дуэлей — тонкий слой над DuelService."""
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_duel_service
from app.db.models.user import User
from app.schemas.duel import AnswerIn, DuelOut, LeaderboardEntry
from app.services.duel import DuelService

router = APIRouter(prefix="/duels", tags=["duels"])


@router.post("/queue", response_model=DuelOut)
def queue(
    current: User = Depends(get_current_user),
    service: DuelService = Depends(get_duel_service),
) -> DuelOut:
    return service.find_match(current)


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(
    service: DuelService = Depends(get_duel_service),
) -> list:
    return service.leaderboard()


@router.get("", response_model=list[DuelOut])
def my_duels(
    current: User = Depends(get_current_user),
    service: DuelService = Depends(get_duel_service),
) -> list:
    return service.my_duels(current)


@router.get("/{duel_id}", response_model=DuelOut)
def get_duel(
    duel_id: int,
    service: DuelService = Depends(get_duel_service),
) -> DuelOut:
    return service.get(duel_id)


@router.post("/{duel_id}/answer", response_model=DuelOut)
def answer(
    duel_id: int,
    data: AnswerIn,
    current: User = Depends(get_current_user),
    service: DuelService = Depends(get_duel_service),
) -> DuelOut:
    return service.submit_answer(duel_id, current, data.text)
