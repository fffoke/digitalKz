# ТІЛДЕС — структура проекта и зоны ответственности

Стек: **FastAPI** (бэк) + **Vue.js** (фронт) + **PostgreSQL**.

## Раскладка по людям

| Человек | Папка | Что делает |
|---|---|---|
| Бэк-дев 1 | `backend/app/routers/user/` | API пользовательского интерфейса (обучение, лента, группы) |
| Бэк-дев 2 | `backend/app/routers/admin/` | API админ-панели (дашборд, модерация, статистика) |
| Фронт-дев 1 | `frontend/user-web/` | Vue-приложение для учеников и преподавателей |
| Фронт-дев 2 | `frontend/admin-web/` | Vue-приложение админ-панели |

## Общий код бэкенда (со-владение двух бэк-девов)

Чтобы не дублировать работу с одной БД:

- `backend/app/db/models/` — SQLAlchemy модели таблиц (`users`, `posts`, `teachers`, `ratings`, ...)
- `backend/app/db/repositories/` — доступ к данным (репозитории)
- `backend/app/services/` — бизнес-логика
- `backend/app/schemas/` — Pydantic-схемы (валидация запросов/ответов)
- `backend/app/core/` — конфиг, авторизация, безопасность

> Каждый бэк-дев пишет **свои ручки** в своём `routers/`, но переиспользует общие
> модели/сервисы/репозитории. Перед добавлением новой модели — согласовать с напарником.

## Структура

```
backend/
  app/
    db/
      models/          # SQLAlchemy модели            (общее)
      repositories/    # репозитории                  (общее)
      session.py       # подключение к БД
    services/          # бизнес-логика                (общее)
    schemas/           # Pydantic-схемы               (общее)
    routers/
      user/            # ручки пользователя           ← бэк-дев 1
      admin/           # ручки админки                ← бэк-дев 2
    core/              # конфиг, auth
    main.py            # точка входа
  migrations/          # alembic
  requirements.txt
frontend/
  user-web/            # Vue                          ← фронт-дев 1
  admin-web/           # Vue                          ← фронт-дев 2
```

## Запуск бэкенда

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Фронтенды инициализируются отдельно в своих папках:
```bash
cd frontend/user-web   # или admin-web
npm create vue@latest .
```
