"""Распознавание речи (казахский) через faster-whisper.

Модель грузится ОДИН раз (ленивый синглтон) и переиспользуется на всех запросах —
иначе при каждом вызове съедается память и Mac начинает лагать.

compute_type="int8" — квантизация: меньше RAM и быстрее на CPU без заметной
потери качества. Для теста/экзамена этого достаточно.
"""
from functools import lru_cache

from faster_whisper import WhisperModel

# "turbo" — то же качество, что тебе понравилось, но легче и быстрее через int8.
# Если Mac всё ещё тяжело тянет — поменяй на "small".
MODEL_SIZE = "turbo"


@lru_cache(maxsize=1)
def _get_model() -> WhisperModel:
    """Грузит модель один раз за всё время жизни процесса."""
    return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")


def transcribe_kazakh(audio_path: str) -> str:
    """Возвращает распознанный текст на казахском из аудиофайла.

    audio_path — путь к .wav/.mp3/.ogg/.flac (ffmpeg должен быть установлен).
    """
    model = _get_model()
    segments, _info = model.transcribe(audio_path, language="kk", beam_size=5)
    return " ".join(segment.text.strip() for segment in segments).strip()
