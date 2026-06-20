# ТІЛДЕС — Админ-панель (под AI-собеседника): аналитика и статистика

Продукт развернулся: ядро — **разговорная практика казахского с ИИ**. Значит и
админка теперь не про модерацию постов, а про **аналитику обучения**: как люди
занимаются, насколько растут в языке, что мешает, что популярно.

Отдельное приложение `frontend/admin-web` (Vue, desktop-first, sidebar-layout) +
бэкенд `backend/app/routers/admin/*`. Слои те же: **Repository → Service → Router**.

> MVP, без переусложнения. Где реальных данных пока мало — отдаём честные нули,
> а не выдуманные графики. Тяжёлые агрегаты считаем простыми SQL `GROUP BY`.

---

## 1. Доступ
- Админ — обычный `User` с `role = admin`. Логин через тот же `POST /api/auth/login`.
- Гард `require_admin` в `core/deps.py` (по аналогии с `require_teacher`); все
  `/api/admin/*` под ним.
- Первого админа: `UPDATE users SET role='admin' WHERE email='...';`

---

## 2. Разделы (боковое меню)

| Раздел | Маршрут | Суть |
|---|---|---|
| 📊 Обзор | `/` | Сводка: пользователи, активность, язык — ключевые KPI |
| 👥 Пользователи | `/users` | Рост, активность, удержание, список |
| 🎤 Активность | `/activity` | Сессии, голосовые, минуты речи |
| 📈 Прогресс языка | `/language` | Распределение уровней, рост, качество речи |
| 🗂 Задания | `/tasks` | Популярные сценарии, проходимость, сложность |
| 🧭 Интересы | `/interests` | Что и зачем учат (мотивация/темы/контексты) |
| ⚙️ Система (LLM/STT) | `/system` | Латентность, ошибки, объёмы вызовов модели |

Идея: **каждый раздел — это набор графиков + таблица**. Везде фильтр по периоду
(сегодня / 7 дней / 30 дней / всё время).

---

## 3. Разделы детально + метрики + endpoints

### 3.1 📊 Обзор (`/`)
Карточки-KPI (число + дельта к прошлому периоду):
- Всего пользователей, новых за период
- Активных за период (запускали сессию)
- Сессий проведено, % завершённых
- Средний балл выполнения / качества казахского
- Минут речи записано

И 2 мини-графика: регистрации по дням, сессии по дням.

- `GET /api/admin/overview?period=7d`
  → `{ users, users_new, active, sessions, sessions_done, completion_rate,
       avg_task_score, avg_language_score, speech_minutes,
       signups_series:[{date,count}], sessions_series:[{date,count}] }`

### 3.2 👥 Пользователи (`/users`)
- **Рост**: график регистраций по дням.
- **Удержание (retention)**: воронка
  `зарегистрировался → прошёл онбординг → 1-я сессия → 1-я завершённая → вернулся (2+ дня)`.
- **Активность**: DAU/WAU (заходившие/занимавшиеся).
- Таблица пользователей: имя, уровень, сессий, последняя активность, дата регистрации.

- `GET /api/admin/users/growth?period=30d` → `[{date, count}]`
- `GET /api/admin/users/funnel?period=30d`
  → `{ registered, onboarded, first_session, first_finished, returned }`
- `GET /api/admin/users/activity?period=30d` → `{ dau:[{date,count}], wau }`
- `GET /api/admin/users?search=&sort=last_active_desc&page=1`
  → `[{ id, name, level, sessions_count, last_active_at, registered_at }]`

### 3.3 🎤 Активность (`/activity`)
Как именно занимаются:
- Сессий начато/завершено по дням (две линии).
- **% завершения** (finished / started) — главный показатель вовлечённости.
- Голосовых сообщений всего, **среднее на сессию**.
- **Минуты речи** записано (суммарная длительность голосовых) — по дням.
- Средняя длина сессии (число реплик) и средняя длительность.
- Активность по часам суток (когда занимаются) — bar 0–23.

- `GET /api/admin/activity/sessions?period=30d`
  → `{ started:[{date,count}], finished:[{date,count}], completion_rate }`
- `GET /api/admin/activity/voice?period=30d`
  → `{ total_messages, avg_per_session, minutes_series:[{date,minutes}] }`
- `GET /api/admin/activity/by-hour?period=30d` → `[{hour, count}]`

### 3.4 📈 Прогресс языка (`/language`)
Главная «образовательная» ценность:
- **Распределение по уровням** A1..C1 (bar) — сколько на каждом. Переключатель
  количество ↔ процент.
- **Повышения уровня** за период (сколько человек выросли).
- **Качество казахского** — средний language_score по дням (растёт ли в среднем).
- **Средний балл выполнения заданий** по дням.
- Топ частых ошибок (агрегат из разборов результата) — если успеем парсить.

- `GET /api/admin/language/levels` → `{ A1, A2, B1, B2, C1, total }`
- `GET /api/admin/language/levelups?period=30d` → `[{date, count}]`
- `GET /api/admin/language/scores?period=30d`
  → `{ language:[{date,avg}], task:[{date,avg}] }`
- `GET /api/admin/language/mistakes?period=30d` → `[{ tag, count }]` *(опц.)*

### 3.5 🗂 Задания (`/tasks`)
Что работает в контенте:
- **Топ сценариев** по запускам (какие темы выбирают).
- **Проходимость** каждого типа: started / finished / средний балл.
- **Распределение по сложности** (easy/medium/hard) и средний балл по сложности.
- Самые «трудные» задания (низкий средний task_score) — кандидаты на доработку
  промптов генерации.

- `GET /api/admin/tasks/top?period=30d&limit=20`
  → `[{ title, started, finished, avg_score }]`
- `GET /api/admin/tasks/difficulty` → `[{ difficulty, count, avg_score }]`
- `GET /api/admin/tasks/hardest?limit=10` → `[{ title, avg_score, attempts }]`

### 3.6 🧭 Интересы (`/interests`)
Голос аудитории — для контента и маркетинга:
- **Зачем учат** (мотивация): работа/переезд/семья/культура/путешествия/учёба — bar.
- **Темы интересов**: спорт, IT, кулинария… — bar/облако.
- **Где пригодится** (контексты): работа/базар/семья/госуслуги… — bar.
- Можно скрестить: например, какой средний прогресс у «работа» vs «семья».

- `GET /api/admin/interests/motivation` → `[{ key, count }]`
- `GET /api/admin/interests/topics` → `[{ topic, count }]`
- `GET /api/admin/interests/contexts` → `[{ key, count }]`

### 3.7 ⚙️ Система — LLM/STT (`/system`)
Операционное здоровье (важно, т.к. модель локальная):
- **Латентность LLM** (среднее/95-й перцентиль время ответа) по дням.
- **Латентность Whisper** (расшифровка) по дням.
- Объёмы: вызовов LLM, расшифровок — по дням.
- **Ошибки**: доля упавших сообщений/оценок (таймауты, сбои модели).
- (если считаем) сумма обработанных аудио-минут — нагрузка на STT.

- `GET /api/admin/system/latency?period=7d`
  → `{ llm:[{date,avg,p95}], stt:[{date,avg,p95}] }`
- `GET /api/admin/system/volume?period=7d`
  → `{ llm_calls:[{date,count}], transcriptions:[{date,count}], error_rate }`

> Для этого в моделях `Turn`/`Session` полезно сохранять `latency_ms`,
> `audio_seconds`, флаг ошибки — дёшево добавить и сразу даёт аналитику.

---

## 4. Полный список admin-endpoints

```
POST   /api/auth/login                       (общий, дальше всё под require_admin)

GET    /api/admin/overview

GET    /api/admin/users/growth
GET    /api/admin/users/funnel
GET    /api/admin/users/activity
GET    /api/admin/users

GET    /api/admin/activity/sessions
GET    /api/admin/activity/voice
GET    /api/admin/activity/by-hour

GET    /api/admin/language/levels
GET    /api/admin/language/levelups
GET    /api/admin/language/scores
GET    /api/admin/language/mistakes        (опц.)

GET    /api/admin/tasks/top
GET    /api/admin/tasks/difficulty
GET    /api/admin/tasks/hardest

GET    /api/admin/interests/motivation
GET    /api/admin/interests/topics
GET    /api/admin/interests/contexts

GET    /api/admin/system/latency
GET    /api/admin/system/volume
```

Общий формат фильтра: `?period=today|7d|30d|all` (бэк превращает в диапазон дат).

---

## 5. Структура admin-web (Vue)

```
src/
  main.js, App.vue
  axios/axios.js                 Bearer-токен (как в user-web)
  router/router.js               гард role=admin
  stores/{admin,ui}.js
  services/
    auth.js
    overview.js  users.js  activity.js  language.js  tasks.js  interests.js  system.js
  components/
    layout/
      AdminLayout.vue            sidebar + topbar + <slot>
      Sidebar.vue                7 разделов
    common/
      StatCard.vue               KPI: число + дельта
      PeriodFilter.vue           today/7d/30d/all
      DataTable.vue              таблица (поиск/сортировка/пагинация)
      EmptyState.vue             честный «данных пока нет»
    charts/
      LineChart.vue              ряды по дням (рост, баллы, латентность)
      BarChart.vue               распределения (уровни, интересы, по часам)
      FunnelChart.vue            воронка удержания
  pages/
    auth/login.vue
    overview.vue                 /
    users.vue                    /users
    activity.vue                 /activity
    language.vue                 /language
    tasks.vue                    /tasks
    interests.vue                /interests
    system.vue                   /system
```

Графики: лёгкая либа — **Chart.js** (`vue-chartjs`) или **ECharts**. Берём одну,
3 обёртки (Line/Bar/Funnel) переиспользуем везде.

---

## 6. Структура admin-api (бэкенд, слои)

```
routers/admin/
  router.py                  агрегатор
  overview.py
  users.py
  activity.py
  language.py
  tasks.py
  interests.py
  system.py
db/repositories/
  analytics.py               агрегирующие SQL-запросы (GROUP BY date/level/...)
services/
  analytics.py               считает периоды, дельты, воронку, перцентили
core/deps.py
  + require_admin            гард + get_analytics_service
```

> Один `AnalyticsService` поверх `AnalyticsRepository` закрывает почти все ручки —
> различаются только агрегаты. Не плодим по сервису на эндпоинт.

---

## 7. Что добавить в модели ради аналитики (дёшево)
- `Session`: `finished_at`, длительность считается из turns.
- `Turn`: `audio_seconds` (длина голосового), `latency_ms` (время ответа ИИ),
  `failed` (bool) — для разделов Активность и Система.
- `Result`: уже есть `task_score`, `language_score` — для Прогресса языка.
- `User`: `last_active_at` (обновлять при действии) — для DAU/удержания.
- `LearningProfile`: `motivation`, `interests`, `contexts` — для раздела Интересы.

---

## 8. Порядок сборки
1. **Гард + Обзор** — `require_admin`, `GET /api/admin/overview`, `AdminLayout`+Sidebar,
   `StatCard` + `LineChart` (каркас и первые KPI).
2. **Пользователи** — рост, воронка удержания, таблица. Самая ценная аналитика роста.
3. **Активность** + **Прогресс языка** — вовлечённость и образовательный эффект (ядро ценности).
4. **Задания** + **Интересы** — продуктовые инсайты для контента.
5. **Система (LLM/STT)** — когда добавим `latency_ms`/`audio_seconds` в `Turn`.

Первого админа: `UPDATE users SET role='admin' WHERE email='твой@email';`
```
