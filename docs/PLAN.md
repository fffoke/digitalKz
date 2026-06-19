# ТІЛДЕС — План: пользовательский фронт + endpoints

Документ для команды. Привязка экранов (Vue, `frontend/user-web`) к ручкам бэка
(FastAPI, `backend/app/routers/user`). В конце — вкладка «Материалы» и экзамены
в админке (`admin-web` + `routers/admin`).

Базовый префикс пользователя: `/api`. Админки: `/api/admin`.

---

## 1. Навигация пользовательского приложения

Нижнее меню (5 вкладок, как на макетах):

| Вкладка | Маршрут | Экран |
|---|---|---|
| 🏠 Дом | `/` | Лента (Threads) |
| ✉️ Директ | `/messages` | Сообщения |
| 📖 Обучение | `/learn` | Роль → дашборд ученика / преподавателя |
| 🔔 Активность | `/activity` | Уведомления |
| 👤 Профиль | `/profile` | Профиль |

Вне меню (онбординг/вложенные):
`/login`, `/register`, `/verify`, `/onboarding/test`,
`/groups/find`, `/groups/create`, `/groups/:id`, `/homework/:id`,
`/exam/:level`, `/u/:username`, `/messages/:dialogId`.

---

## 2. Экраны и их endpoints

### 2.1 Аутентификация и онбординг

**`/register` — регистрация (выбор роли Ученик/Преподаватель)**
- `POST /api/auth/register` — { name, email, password, role }

**`/login`**
- `POST /api/auth/login` → JWT
- `GET /api/auth/me` — текущий пользователь (вызывается на каждом старте app)

**`/verify` — верификация личности (ИИН + удостоверение)**
- `POST /api/verification` — { iin, doc_photo } → статус `pending`
- `GET /api/verification/status` — pending / approved / rejected

**`/onboarding/test` — вступительный тест (25 вопросов)**
- `GET /api/entrance-exam` — отдаёт вопросы (текст + 2-3 голосовых + 1 запись чтения)
- `POST /api/entrance-exam/submit` — { answers[], audio_files[] }
  → бэк прогоняет голос через `services/transcription.py` (whisper) + LLM
  → возвращает уровень `A1..C1` и ранг `Бастауыш`

---

### 2.2 🏠 Дом — Лента

**`/` — лента постов**
- `GET /api/posts?cursor=` — лента (пагинация)
- `POST /api/posts` — создать пост (только казахский → модерация языка)
- `POST /api/posts/:id/like` / `DELETE /api/posts/:id/like`
- `POST /api/posts/:id/repost`
- `POST /api/posts/:id/report` — { reason }

**`/post/:id` — пост с комментариями**
- `GET /api/posts/:id`
- `GET /api/posts/:id/comments`
- `POST /api/posts/:id/comments` — { text }

---

### 2.3 ✉️ Директ — Сообщения

**`/messages` — список диалогов**
- `GET /api/conversations`

**`/messages/:dialogId` — чат**
- `GET /api/conversations/:id/messages?cursor=`
- `POST /api/conversations/:id/messages` — { text }
- `POST /api/conversations` — начать диалог { user_id }

---

### 2.4 📖 Обучение — РЕЖИМ УЧЕНИКА

**`/learn` (ученик) — дашборд** (макет: прогресс, streak, группа, карта, план, экзамен)
- `GET /api/me/dashboard` — { level, rank, progress_percent, days_to_exam, lessons_count, homework_done/total, streak }
- `GET /api/me/group` — текущая группа { name, schedule, next_lesson, zoom_link }
- `GET /api/me/group/plan` — план группы (секции → этапы, статусы ✓/текущий/🔒)
- `GET /api/me/group/progress` — карта прогресса (узлы карты)
- `GET /api/me/homework/current` — текущее ДЗ { title, due, status }
- `GET /api/groups/recommended` — «Найдите свою группу» (уровень ±1)

**`/groups/find` — выбор группы**
- `GET /api/groups/recommended?schedule=` — фильтр по расписанию
- `POST /api/groups/:id/join`

**`/groups/create` — создать свою группу**
- `POST /api/groups` — { level, schedule } → возвращает invite-ссылку
- `POST /api/groups/:id/invite` — пригласить друзей

**`/groups/:id` — страница группы (чат, план, карта, ДЗ)**
- `GET /api/groups/:id`
- `GET /api/groups/:id/chat` / `POST /api/groups/:id/chat`
  (доступ к чату открывается за 6 ч до урока; Zoom-ссылка падает сюда автоматически)

**`/homework/:id` — задание ДЗ**
- `GET /api/homework/:id`
- `POST /api/homework/:id/submit` — { text / audio }

**`/exam/:level` — экзамен на уровень (20 вопросов + голос)**
- `GET /api/me/exam-eligibility` — можно ли сдавать (авто по завершении потока / досрочно раз в 2 недели)
- `GET /api/exams/level/:level` — вопросы экзамена (берутся из админских)
- `POST /api/exams/:id/submit` — { answers[], audio } → whisper + LLM → вердикт + новый уровень

**Оценка урока (после каждого урока)**
- `POST /api/lessons/:id/rate` — { score 1-5, review_text, anonymous }

---

### 2.5 📖 Обучение — РЕЖИМ ПРЕПОДАВАТЕЛЯ

**Стать преподавателем**
- `POST /api/teacher/apply` — анкета { education, experience, kazakh_level } → модерация + созвон

**`/learn` (преподаватель) — дашборд** (макет: статы, мои группы, доступные группы, уроки, отзывы)
- `GET /api/teacher/dashboard` — { lessons_held, students_total, hours, rank_in_market }
- `GET /api/teacher/groups` — «Мои группы на этой неделе»
- `GET /api/teacher/groups/available` — «Доступные группы без преподавателя» (уровень, секция, этап)
- `POST /api/teacher/groups/:id/take` — «Взять группу»
- `GET /api/teacher/lessons` — «Ближайшие уроки»
- `POST /api/teacher/lessons` — назначить урок { group_id, datetime } (можно на недели вперёд)
- `POST /api/teacher/lessons/:id/cancel` — отменить (лимит N/мес → падает приоритет)
- `POST /api/teacher/lessons/:id/start` — открыть урок (создаёт Zoom-конференцию, кидает ссылку в чат)
- `GET /api/teacher/homework/pending` — ДЗ на проверку (проверяет следующий препод группы)
- `POST /api/teacher/homework/:id/grade` — { score, feedback }
- `GET /api/teacher/reviews` — отзывы учеников

---

### 2.6 🔔 Активность — Уведомления

**`/activity` — лента событий (Все / Подписки / Упоминания)**
- `GET /api/notifications?filter=all|follows|mentions`
- (типы: лайк, подписка, комментарий, упоминание, репост)

---

### 2.7 👤 Профиль

**`/profile` и `/u/:username` — профиль (Посты / Ответы / Репосты)**
- `GET /api/users/:username` — { avatar, bio, rank, followers, following, total_likes }
- `GET /api/users/:username/posts`
- `GET /api/users/:username/replies`
- `GET /api/users/:username/reposts`
- `POST /api/users/:id/follow` / `DELETE /api/users/:id/follow`

**`/profile/edit`**
- `PATCH /api/profile` — { avatar, name, bio }

---

## 3. Сводный список endpoints пользователя (`routers/user`)

```
# auth
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
POST   /api/verification
GET    /api/verification/status

# вступительный тест
GET    /api/entrance-exam
POST   /api/entrance-exam/submit

# лента
GET    /api/posts
POST   /api/posts
GET    /api/posts/{id}
POST   /api/posts/{id}/like
DELETE /api/posts/{id}/like
POST   /api/posts/{id}/repost
POST   /api/posts/{id}/report
GET    /api/posts/{id}/comments
POST   /api/posts/{id}/comments

# директ
GET    /api/conversations
POST   /api/conversations
GET    /api/conversations/{id}/messages
POST   /api/conversations/{id}/messages

# обучение (ученик)
GET    /api/me/dashboard
GET    /api/me/group
GET    /api/me/group/plan
GET    /api/me/group/progress
GET    /api/me/homework/current
GET    /api/groups/recommended
POST   /api/groups
POST   /api/groups/{id}/join
POST   /api/groups/{id}/invite
GET    /api/groups/{id}
GET    /api/groups/{id}/chat
POST   /api/groups/{id}/chat
GET    /api/homework/{id}
POST   /api/homework/{id}/submit
GET    /api/me/exam-eligibility
GET    /api/exams/level/{level}
POST   /api/exams/{id}/submit
POST   /api/lessons/{id}/rate
GET    /api/materials?level=A2          # потребление материалов из админки

# обучение (преподаватель)
POST   /api/teacher/apply
GET    /api/teacher/dashboard
GET    /api/teacher/groups
GET    /api/teacher/groups/available
POST   /api/teacher/groups/{id}/take
GET    /api/teacher/lessons
POST   /api/teacher/lessons
POST   /api/teacher/lessons/{id}/cancel
POST   /api/teacher/lessons/{id}/start
GET    /api/teacher/homework/pending
POST   /api/teacher/homework/{id}/grade
GET    /api/teacher/reviews

# активность / профиль
GET    /api/notifications
GET    /api/users/{username}
GET    /api/users/{username}/posts
GET    /api/users/{username}/replies
GET    /api/users/{username}/reposts
POST   /api/users/{id}/follow
DELETE /api/users/{id}/follow
PATCH  /api/profile
```

---

## 4. Админка — вкладка «Материалы» и Экзамены (`routers/admin`)

Новая вкладка в админ-панели. Материалы и экзамены создаются здесь и
**потребляются** пользовательским фронтом (`GET /api/materials`, `GET /api/exams/level/{level}`, `GET /api/entrance-exam`).

### Страницы админки
- `/admin/materials` — список + создание материалов по уровням
- `/admin/materials/new` — форма материала (уровень, секция, этап, контент)
- `/admin/exams` — список экзаменов
- `/admin/exams/new` — конструктор экзамена (уровень + вопросы + голосовое задание)
- `/admin/exams/entrance` — настройка вступительного теста (25 вопросов)

### Endpoints
```
# материалы (по уровням A1..C1)
GET    /api/admin/materials?level=A2
POST   /api/admin/materials          # { level, section, stage, title, content }
PATCH  /api/admin/materials/{id}
DELETE /api/admin/materials/{id}

# экзамены на уровень (20 вопросов + голос)
GET    /api/admin/exams
POST   /api/admin/exams              # { target_level, questions[], voice_task }
PATCH  /api/admin/exams/{id}
DELETE /api/admin/exams/{id}
POST   /api/admin/exams/{id}/questions

# вступительный экзамен (25 вопросов, общий)
GET    /api/admin/entrance-exam
PUT    /api/admin/entrance-exam      # вопросы + голосовые + задание на чтение
```

Связка: админ создаёт экзамен на уровень → ученик получает его через
`GET /api/exams/level/{level}`; вступительный → `GET /api/entrance-exam`;
материалы уровня → `GET /api/materials?level=`.

---

## 5. Модели БД (черновик, `db/models/`, со-владение)

```
User(id, name, email, password_hash, role, avatar, bio, rank, level, created_at)
Verification(id, user_id, iin, doc_url, status)
Post(id, author_id, text, created_at)  +  Like, Repost, Comment, Report
Follow(follower_id, following_id)
Conversation, Message
Group(id, level, schedule, invite_code, teacher_id, section, stage)
GroupMember(group_id, user_id)
Lesson(id, group_id, teacher_id, datetime, zoom_link, status)
LessonRating(lesson_id, student_id, score, review, anonymous)
Homework(id, group_id, student_id, task, submission, grade, feedback, graded_by)
Plan / Section / Stage(group_id, order, title, status)
Material(id, level, section, stage, title, content)      # ← из админки
Exam(id, target_level | entrance, questions(json), voice_task)  # ← из админки
ExamAttempt(id, exam_id, user_id, answers, verdict, result_level)
Notification(id, user_id, type, actor_id, post_id, read, created_at)
TeacherApplication(id, user_id, education, experience, kazakh_level, status)
```

---

## 6. Привязка к команде

| Человек | Зона |
|---|---|
| Фронт-дев 1 | `user-web`: Дом, Директ, Обучение(ученик+препод), Активность, Профиль |
| Бэк-дев 1 | `routers/user/*` + общие сервисы (лента, группы, уроки, экзамены, whisper+LLM) |
| Фронт-дев 2 | `admin-web`: дашборд, модерация, преподаватели, ученики, **Материалы**, Экзамены |
| Бэк-дев 2 | `routers/admin/*` (модерация, аналитика, материалы, конструктор экзаменов) |

Общий слой `db/models`, `schemas`, `services` — со-владение бэк-девов.

---

## 7. Следующие шаги
1. Завести модели в `db/models/` + первая миграция Alembic.
2. Поднять auth (`/auth/register`, `/login`, JWT, `/me`).
3. Лента + профиль (самое наглядное для демо).
4. Обучение: дашборд ученика → группы → ДЗ → экзамен (whisper+LLM уже готов).
5. Админка: Материалы и конструктор экзаменов → их сразу потребляет п.4.
```
