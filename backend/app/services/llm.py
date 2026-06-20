"""LLM AI-собеседника — три роли за одним интерфейсом, провайдер сменный.

Роли (намеренно раздельные методы — позже любую можно увести на модель посильнее):
  * generate_tasks — из интересов делает задания-сценарии
  * reply          — отвечает в диалоге на казахском (роль из scenario)
  * evaluate       — оценивает выполнение задания и качество казахского

Контекст НЕ хранится в модели: история диалога приходит в reply()/evaluate()
параметром (её собирает TutorService из таблицы Turn).

Провайдер выбирается settings.LLM_PROVIDER:
  * "stub"   — без модели, эвристики/шаблоны (фронт работает сразу)
  * "ollama" — локальная KazLLM через Ollama (http://host:11434)
"""
from __future__ import annotations

import json
import urllib.request
from abc import ABC, abstractmethod

from app.core.config import settings

# history: список реплик в формате чата — {"role": "user"|"assistant", "content": str}
Message = dict[str, str]

# жёсткое правило для ответов собеседника (добавляется к scenario в reply)
_REPLY_RULES = (
    "\n\nВАЖНО: отвечай ТОЛЬКО на казахском языке, 1–2 короткими предложениями, "
    "оставайся в роли. Не используй русский. НИКОГДА не пиши плейсхолдеры в "
    "скобках вроде [имя]. НЕ обращайся к ученику по имени и НЕ придумывай ему имя — "
    "ты не знаешь, как его зовут. Имя можно придумать ТОЛЬКО для своего персонажа "
    "(если нужно представиться). Если ученик ещё не поздоровался — поздоровайся первым."
)


class BaseLLM(ABC):
    @abstractmethod
    def generate_tasks(self, *, motivation: str, interests: list[str],
                       contexts: list[str], level: str,
                       case_text: str = "") -> list[dict]:
        """→ [{title, scenario, context, difficulty}, ...] — 3 задания
        (easy/medium/hard) откалиброванные под уровень ученика."""

    @abstractmethod
    def reply(self, *, scenario: str, history: list[Message]) -> str:
        """Ответ собеседника на казахском. history уже включает последнюю реплику."""

    @abstractmethod
    def evaluate(self, *, scenario: str, title: str, history: list[Message]) -> dict:
        """→ {task_score:int, language_score:int, feedback:str}"""


# --------------------------------------------------------------------------- #
# Заглушка — пока модель не подключена. Реалистичная, чтобы можно было кликать.
# --------------------------------------------------------------------------- #
# (title, scenario для ИИ, goal — понятное описание-задача для пользователя)
_CONTEXT_SCENARIOS = {
    "work":   ("Разговор с коллегой",
               "Ты — казахоязычный коллега на работе. Цель ученика — обсудить рабочую задачу.",
               "Поздоровайтесь с коллегой по-казахски, расскажите над чем работаете "
               "и спросите его мнение. Поддержите диалог 3–4 репликами."),
    "bazaar": ("Покупка на базаре",
               "Ты — продавец на базаре в Алматы. Цель ученика — спросить цену и поторговаться.",
               "Подойдите к продавцу, поздоровайтесь, спросите цену товара и попробуйте "
               "поторговаться по-казахски. Договоритесь о покупке."),
    "family": ("Разговор в семье",
               "Ты — родственник за ужином. Цель ученика — поддержать беседу о дне.",
               "Поговорите с родственником за ужином: расскажите, как прошёл ваш день, "
               "и расспросите про его дела на казахском."),
    "gov":    ("В госуслугах (ЦОН)",
               "Ты — оператор в ЦОНе. Цель ученика — оформить простую справку.",
               "Обратитесь к оператору ЦОНа: поздоровайтесь, объясните какую справку "
               "хотите получить и уточните, что нужно для этого."),
    "travel": ("В путешествии",
               "Ты — местный житель. Цель ученика — спросить дорогу и совет.",
               "Спросите у местного жителя дорогу до нужного места и попросите совет, "
               "что посмотреть рядом — всё по-казахски."),
    "friends":("Беседа с другом",
               "Ты — близкий друг. Цель ученика — рассказать, как прошёл день.",
               "Поболтайте с другом по-казахски: расскажите свои новости и расспросите "
               "о его планах на выходные."),
}
_RULES = ("Говори ТОЛЬКО на казахском под уровень {level}. "
          "Не переходи на русский. Будь дружелюбным, задавай по одному вопросу.")

# три задания на один уровень — отличаются сложностью В РАМКАХ уровня
_DIFFICULTY_TIERS = [
    ("easy", "Лёгкое", "короткий простой диалог, базовые фразы"),
    ("medium", "Среднее", "диалог чуть длиннее, пара уточняющих вопросов"),
    ("hard", "Сложное", "более развёрнутый диалог с непредвиденным поворотом"),
]

_STUB_REPLIES = [
    "Сәлеметсіз бе! Қалыңыз қалай?",
    "Жақсы екен! Тағы не айта аласыз?",
    "Өте жақсы! Неге олай ойлайсыз?",
    "Түсіндім. Соны толығырақ айтып бересіз бе?",
    "Жарайды, рахмет! Әңгімеңіз тамаша болды.",
]


class StubLLM(BaseLLM):
    def generate_tasks(self, *, motivation, interests, contexts, level, case_text=""):
        chosen = contexts or ["friends"]
        tasks = []
        # одно задание на каждую ступень сложности, всё под один уровень
        for i, (diff, label, hint) in enumerate(_DIFFICULTY_TIERS):
            ctx = chosen[i % len(chosen)]
            title, scenario, goal = _CONTEXT_SCENARIOS.get(ctx, _CONTEXT_SCENARIOS["friends"])
            topic = interests[i % len(interests)] if interests else None
            if topic:
                scenario += f" По возможности затроньте тему «{topic}»."
                goal += f" Можно поговорить о «{topic}»."
            if case_text:
                scenario += f" Учитывай ситуацию ученика: {case_text}."
            tasks.append({
                "title": f"{title} ({label.lower()})",
                "scenario": (
                    f"{scenario} Уровень сложности: {hint}. "
                    + _RULES.format(level=level)
                ),
                "description": goal,
                "context": f"Уровень {level} · {label.lower()}",
                "difficulty": diff,
            })
        return tasks

    def reply(self, *, scenario, history):
        user_turns = sum(1 for m in history if m["role"] == "user")
        idx = min(user_turns, len(_STUB_REPLIES) - 1)
        return _STUB_REPLIES[idx]

    def evaluate(self, *, scenario, title, history):
        # ВНИМАНИЕ: это плейсхолдер без модели — рубрикатор по длине/разнообразию речи.
        # Намеренно НЕ выдаёт 100 (потолок 88), чтобы не путать с реальной оценкой.
        # Полноценную оценку даёт OllamaLLM (KazLLM).
        user_msgs = [m["content"].strip() for m in history if m["role"] == "user" and m["content"].strip()]
        if not user_msgs:
            return {
                "task_score": 0,
                "language_score": 0,
                "feedback": "Вы не сказали ни одной реплики. Запишите голосовое и попробуйте снова.",
            }

        all_words = " ".join(user_msgs).split()
        total = len(all_words)
        unique = len(set(w.lower() for w in all_words))
        avg_per_turn = total / len(user_msgs)
        variety = unique / total if total else 0   # 0..1 — насколько разнообразна лексика

        # SpeakingScore: длина реплик (до ~6 слов = норма) + разнообразие лексики
        length_part = min(45, avg_per_turn / 6 * 45)
        variety_part = variety * 35
        language_score = min(88, round(15 + length_part + variety_part))

        # выполнение: число содержательных реплик (4 обмена ≈ полный сценарий)
        task_score = min(88, round(len(user_msgs) / 4 * 88))

        return {
            "task_score": task_score,
            "language_score": language_score,
            "feedback": (
                f"Реплик: {len(user_msgs)}, слов: {total}, уникальных: {unique}. "
                "Старайтесь говорить развёрнутее и использовать больше разных слов. "
                "⚠️ Это предварительная оценка без AI-модели — подключите KazLLM для "
                "полноценного разбора грамматики и естественности речи."
            ),
        }


# --------------------------------------------------------------------------- #
# Ollama — локальная KazLLM. Без сторонних зависимостей (stdlib urllib).
# --------------------------------------------------------------------------- #
class OllamaLLM(BaseLLM):
    def __init__(self) -> None:
        self.base = settings.LLM_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL

    def _chat(self, messages: list[Message], *, as_json: bool = False,
              timeout: int = 120) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.7},
        }
        if as_json:
            payload["format"] = "json"
        req = urllib.request.Request(
            f"{self.base}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        return data["message"]["content"].strip()

    def generate_tasks(self, *, motivation, interests, contexts, level, case_text=""):
        system = (
            "Ты — методист, который составляет задания для разговорной практики "
            "казахского языка. Верни СТРОГО JSON вида "
            '{"tasks":[{"title":"...","scenario":"...","description":"...",'
            '"context":"...","difficulty":"easy|medium|hard"}]}. '
            "Сделай РОВНО 3 задания — по одному на сложность easy, medium, hard, — "
            f"но ВСЕ откалибруй под уровень ученика {level} (easy/medium/hard — это "
            f"относительная сложность В РАМКАХ уровня {level}, не выше). "
            "Поле scenario — инструкция собеседнику-ИИ: его роль, цель ученика и "
            f"правило говорить только на казахском под уровень {level}. "
            "Поле description — понятное задание ДЛЯ УЧЕНИКА на русском (2–3 "
            "предложения): что сделать, о чём поговорить, какая цель диалога. "
            "title — короткое название, context — очень короткий тег. Всё на русском."
        )
        user = (
            f"Уровень ученика: {level}. Мотивация: {motivation}. "
            f"Интересы: {', '.join(interests) or '—'}. "
            f"Где пригодится: {', '.join(contexts) or '—'}."
        )
        if case_text:
            user += f"\nСитуация ученика (подгони задания под неё): {case_text}"
        raw = self._chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            as_json=True,
        )
        data = json.loads(raw)
        tasks = data.get("tasks", data if isinstance(data, list) else [])
        return tasks

    def reply(self, *, scenario, history):
        messages = [{"role": "system", "content": scenario + _REPLY_RULES}, *history]
        return self._chat(messages)

    def evaluate(self, *, scenario, title, history):
        transcript = "\n".join(
            f"{'Ученик' if m['role'] == 'user' else 'Собеседник'}: {m['content']}"
            for m in history
        )
        system = (
            "Ты — экзаменатор казахского языка. Оцени диалог. Верни СТРОГО JSON: "
            '{"task_score":0-100,"language_score":0-100,"feedback":"..."}. '
            "task_score — насколько ученик достиг цели задания. "
            "language_score — качество казахского (грамматика, лексика, естественность). "
            "feedback — короткий разбор на русском: что хорошо и как сказать лучше."
        )
        user = f"Задание: {title}\nЦель/роль: {scenario}\n\nДиалог:\n{transcript}"
        raw = self._chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            as_json=True,
        )
        data = json.loads(raw)
        return {
            "task_score": int(data.get("task_score", 0)),
            "language_score": int(data.get("language_score", 0)),
            "feedback": data.get("feedback", ""),
        }


# --------------------------------------------------------------------------- #
# OpenAI — облако (gpt-4o-mini). Дёшево, хорошо знает казахский. Через httpx.
# --------------------------------------------------------------------------- #
class OpenAILLM(BaseLLM):
    def __init__(self) -> None:
        self.base = settings.OPENAI_BASE_URL.rstrip("/")
        self.model = settings.OPENAI_MODEL
        self.key = settings.OPENAI_API_KEY

    def _chat(self, messages: list[Message], *, as_json: bool = False,
              timeout: int = 60) -> str:
        import httpx

        payload: dict = {"model": self.model, "messages": messages, "temperature": 0.7}
        if as_json:
            payload["response_format"] = {"type": "json_object"}
        r = httpx.post(
            f"{self.base}/chat/completions",
            headers={"Authorization": f"Bearer {self.key}"},
            json=payload,
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    def generate_tasks(self, *, motivation, interests, contexts, level, case_text=""):
        system = (
            "Ты — методист, составляешь задания для разговорной практики казахского. "
            'Верни СТРОГО JSON {"tasks":[{"title","scenario","description","context",'
            '"difficulty":"easy|medium|hard"}]}. Ровно 3 задания (easy/medium/hard), '
            f"все под уровень {level}. scenario — инструкция собеседнику-ИИ (роль, цель, "
            f"говорить только по-казахски под {level}). description — понятное задание "
            "для ученика на русском (2–3 предложения). title и context — на русском."
        )
        user = (
            f"Уровень: {level}. Мотивация: {motivation}. "
            f"Интересы: {', '.join(interests) or '—'}. "
            f"Контексты: {', '.join(contexts) or '—'}."
        )
        if case_text:
            user += f"\nСитуация ученика: {case_text}"
        raw = self._chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            as_json=True,
        )
        data = json.loads(raw)
        return data.get("tasks", data if isinstance(data, list) else [])

    def reply(self, *, scenario, history):
        return self._chat([{"role": "system", "content": scenario + _REPLY_RULES}, *history])

    def evaluate(self, *, scenario, title, history):
        transcript = "\n".join(
            f"{'Ученик' if m['role'] == 'user' else 'Собеседник'}: {m['content']}"
            for m in history
        )
        system = (
            "Ты — экзаменатор казахского. Верни СТРОГО JSON "
            '{"task_score":0-100,"language_score":0-100,"feedback":"..."}. '
            "task_score — достиг ли ученик цели задания. language_score — качество "
            "казахского (грамматика, лексика, естественность). feedback — короткий "
            "разбор на русском: что хорошо и как сказать лучше."
        )
        user = f"Задание: {title}\nЦель/роль: {scenario}\n\nДиалог:\n{transcript}"
        raw = self._chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            as_json=True,
        )
        data = json.loads(raw)
        return {
            "task_score": int(data.get("task_score", 0)),
            "language_score": int(data.get("language_score", 0)),
            "feedback": data.get("feedback", ""),
        }


_PROVIDERS = {"stub": StubLLM, "ollama": OllamaLLM, "openai": OpenAILLM}


def get_llm() -> BaseLLM:
    """Фабрика по settings.LLM_PROVIDER. Один экземпляр на процесс не нужен —
    провайдеры лёгкие (без состояния)."""
    provider = _PROVIDERS.get(settings.LLM_PROVIDER, StubLLM)
    return provider()
