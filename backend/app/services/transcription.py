"""Распознавание речи (казахский).

Два провайдера (STT_PROVIDER):
  * "local"  — faster-whisper локально (бесплатно, но качество казахского зависит
               от размера модели; small слабый, large-v3 точный но медленный);
  * "openai" — gpt-4o-transcribe в облаке (копейки за минуту, качество выше).

Локальная модель грузится ОДИН раз (ленивый синглтон).
"""
import os
from functools import lru_cache

from faster_whisper import WhisperModel

from app.core.config import settings

# Размер модели регулирует скорость/качество. "turbo" точнее, но тяжёлый на CPU.
# "small" — заметно быстрее, для коротких реплик качество ок. Меняется через env
# WHISPER_MODEL ("base"/"small"/"medium"/"turbo").
MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
# на GPU (WHISPER_DEVICE=cuda) — кратно быстрее и можно брать large-v3
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE", "float16" if DEVICE == "cuda" else "int8")


@lru_cache(maxsize=1)
def _get_model() -> WhisperModel:
    """Грузит модель один раз за всё время жизни процесса (первый вызов — медленный).

    MODEL_SIZE может быть размером ("small"/"large-v3") ИЛИ репозиторием HF с
    CT2-моделью (например, казахско-дообученной) — faster-whisper скачает по токену.
    """
    return WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)


def warmup() -> None:
    """Прогрев локальной модели на старте (только для STT_PROVIDER=local)."""
    if settings.STT_PROVIDER == "local":
        _get_model()


# подсказка модели, что речь казахская (чуть улучшает распознавание)
_KK_PROMPT = "Қазақ тіліндегі сөйлеу. Сәлеметсіз бе. Рахмет."


def _transcribe_local(audio_path: str) -> str:
    model = _get_model()
    segments, _info = model.transcribe(
        audio_path,
        language="kk",
        beam_size=5,
        initial_prompt=_KK_PROMPT,
        condition_on_previous_text=False,
    )
    return " ".join(segment.text.strip() for segment in segments).strip()


def _transcribe_openai(audio_path: str) -> str:
    """gpt-4o-transcribe через OpenAI API (multipart). language=kk для казахского."""
    import httpx

    with open(audio_path, "rb") as f:
        r = httpx.post(
            f"{settings.OPENAI_BASE_URL.rstrip('/')}/audio/transcriptions",
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            data={"model": settings.OPENAI_STT_MODEL, "language": "kk"},
            files={"file": (os.path.basename(audio_path), f, "audio/webm")},
            timeout=60,
        )
    r.raise_for_status()
    return (r.json().get("text") or "").strip()


def transcribe_kazakh(audio_path: str) -> str:
    """Распознаёт казахскую речь. Провайдер — settings.STT_PROVIDER."""
    if settings.STT_PROVIDER == "openai":
        return _transcribe_openai(audio_path)
    return _transcribe_local(audio_path)
