# Инфраструктура — Docker Compose

Поднимает весь стек одной командой: **PostgreSQL + backend (FastAPI) + user-web (Vue)**.
Режим — разработка, с hot-reload по обоим сервисам.

## Запуск

```bash
cd infra
cp .env.example .env        # один раз — задать пароли/секрет
docker compose up --build
```

После старта:

| Сервис | URL |
|---|---|
| Пользовательский фронт (Vite) | http://localhost:5173 |
| API (Swagger) | http://localhost:8000/docs |
| Health-check | http://localhost:8000/health |
| PostgreSQL | localhost:5432 (postgres / пароль из `.env`) |

Таблицы создаются автоматически при старте backend (`python -m app.db.init_db`).

## Полезное

```bash
docker compose up -d --build      # в фоне
docker compose logs -f backend    # логи бэка
docker compose down               # остановить
docker compose down -v            # остановить и стереть БД (volume pgdata)
```

## Замечания

- **Hot-reload:** код примонтирован томами — правки в `backend/app` и
  `frontend/user-web/main/src` подхватываются без пересборки. Пересобирать
  (`--build`) нужно только при изменении зависимостей (`requirements.txt`,
  `package.json`).
- **Модели whisper** кэшируются в томе `hf_cache`, чтобы не качались заново при
  каждом перезапуске backend.
- **Фронт ходит на API по** `http://127.0.0.1:8000` (см. `src/axios/axios.js`) —
  это адрес с точки зрения браузера, работает из коробки.
- **admin-web** добавится в compose, когда наполнят `frontend/admin-web`
  (закомментированный блок уже готов).
