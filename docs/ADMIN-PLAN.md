# ТІЛДЕС — Админ-панель: полный план (admin-web + admin-api)

Отдельное приложение `frontend/admin-web` (Vue, как user-web) + бэкенд в
`backend/app/routers/admin/*`. Слои те же: **Repository → Service → Router**.

Зона ответственности: фронт-дев 2 (`admin-web`), бэк-дев 2 (`routers/admin`,
общие `db/` и `services/` — со-владение).

---

## 1. Доступ и авторизация

- Админ — обычный `User` с `role = admin`. Логин через тот же
  `POST /api/auth/login`.
- Нужен гард `require_admin` в `core/deps.py` (по аналогии с `require_teacher`):
  все ручки `/api/admin/*` защищены им.
- Первого админа создаём сидом/вручную:
  `UPDATE users SET role='admin' WHERE email='...';`
  (позже — CLI-команда `python -m app.scripts.make_admin <email>`).
- Это отдельный сайт (`admin.tildes.kz`), не PWA, desktop-first, **sidebar**-layout
  (не нижнее меню).

---

## 2. Страницы (боковое меню)

| Раздел | Маршрут | Содержимое |
|---|---|---|
| 🔐 Вход | `/login` | Логин админа |
| 📊 Дашборд | `/` | Сводная статистика |
| 🛡 Модерация | `/moderation` | Жалобы + заявки на роли (подвкладки) |
| 📝 Посты | `/posts` | Статистика постов |
| 👨‍🏫 Преподаватели | `/teachers` | Список, поиск, фильтры, карточка |
| 🎓 Ученики | `/students` | Статистика, график, список, бан |
| 📚 Материалы | `/materials` | CRUD материалов по уровням |
| 📋 Экзамены | `/exams` | Конструктор экзаменов + вступительный |

---

## 3. Страницы детально + endpoints

### 3.1 📊 Дашборд (`/`)
Карточки: всего пользователей, учеников, преподавателей — и то же **за сутки**.
- `GET /api/admin/stats`
  → `{ users, students, teachers, users_24h, students_24h, teachers_24h }`

### 3.2 🛡 Модерация (`/moderation`) — подвкладки

**Заявки на роли** (то, что уже частично готово)
- `GET /api/admin/moderation/verifications?status=pending` — заявки учеников
- `POST /api/admin/moderation/verifications/{id}/approve` ✅ есть
- `POST /api/admin/moderation/verifications/{id}/reject`
- `GET /api/admin/moderation/teacher-applications?status=pending`
- `POST /api/admin/moderation/teacher-applications/{id}/approve` ✅ есть
- `POST /api/admin/moderation/teacher-applications/{id}/reject`

**Жалобы на пользователей**
- `GET /api/admin/moderation/users` — список жалоб (причина, дата, автор жалобы)
- `POST /api/admin/users/{id}/warn` — предупреждение
- `POST /api/admin/users/{id}/ban` — блокировка

**Жалобы на посты**
- `GET /api/admin/moderation/posts` — список жалоб (причина, дата)
- `DELETE /api/admin/posts/{id}` — удалить пост
- `POST /api/admin/users/{id}/warn` — предупредить автора

### 3.3 📝 Посты (`/posts`)
- `GET /api/admin/posts/stats`
  → `{ total, posts_24h, avg_activity }` *(avg_activity — заглушка с реалистичными данными)*

### 3.4 👨‍🏫 Преподаватели (`/teachers`)
Список + поиск по имени + фильтры (по средней оценке ↑↓, по дате добавления ↑↓).
- `GET /api/admin/teachers?search=&sort=rating_desc|rating_asc|date_desc|date_asc`
  → `[{ id, name, avg_rating, joined_at }]`

Карточка преподавателя:
- `GET /api/admin/teachers/{id}`
  → `{ name, avg_rating, joined_at, reviews: [{ author_name, score, text, date }] }`
  *(в админке видно, КТО оставил отзыв — даже анонимный)*

### 3.5 🎓 Ученики (`/students`)
Статистика:
- `GET /api/admin/students/stats`
  → `{ level_ups_24h, distribution: { A1, A2, B1, B2, C1 }, total }`
  (фронт сам переключает количество ↔ процент)

Список:
- `GET /api/admin/students?search=&level=A1..C1&sort=date_asc|date_desc`
  → `[{ id, name, level, registered_at, is_banned }]`
- `POST /api/admin/students/{id}/ban`

### 3.6 📚 Материалы (`/materials`)
Создание/редактирование материалов по уровням (A1..C1, секция, этап).
- `GET /api/admin/materials?level=A2`
- `POST /api/admin/materials` — `{ level, section, stage, title, content }`
- `PATCH /api/admin/materials/{id}`
- `DELETE /api/admin/materials/{id}`

### 3.7 📋 Экзамены (`/exams`)
Конструктор экзаменов на уровень + вступительный.
- `GET /api/admin/exams`
- `POST /api/admin/exams` — `{ target_level, title, questions[], voice_task }`
- `PATCH /api/admin/exams/{id}`
- `DELETE /api/admin/exams/{id}`
- `GET /api/admin/entrance-exam` / `PUT /api/admin/entrance-exam` — вступительный (25 вопросов)

Формат вопроса (JSON):
`{ "type": "choice|voice|reading", "text": "...", "options": [...], "answer": "..." }`

---

## 4. Полный список admin-endpoints

```
# auth (общий) + гард require_admin на всё ниже
POST   /api/auth/login

# дашборд
GET    /api/admin/stats

# модерация — заявки
GET    /api/admin/moderation/verifications
POST   /api/admin/moderation/verifications/{id}/approve     ✅
POST   /api/admin/moderation/verifications/{id}/reject
GET    /api/admin/moderation/teacher-applications
POST   /api/admin/moderation/teacher-applications/{id}/approve  ✅
POST   /api/admin/moderation/teacher-applications/{id}/reject

# модерация — жалобы
GET    /api/admin/moderation/users
GET    /api/admin/moderation/posts
POST   /api/admin/users/{id}/warn
POST   /api/admin/users/{id}/ban
DELETE /api/admin/posts/{id}

# посты
GET    /api/admin/posts/stats

# преподаватели
GET    /api/admin/teachers
GET    /api/admin/teachers/{id}

# ученики
GET    /api/admin/students/stats
GET    /api/admin/students
POST   /api/admin/students/{id}/ban

# материалы
GET    /api/admin/materials
POST   /api/admin/materials
PATCH  /api/admin/materials/{id}
DELETE /api/admin/materials/{id}

# экзамены
GET    /api/admin/exams
POST   /api/admin/exams
PATCH  /api/admin/exams/{id}
DELETE /api/admin/exams/{id}
GET    /api/admin/entrance-exam
PUT    /api/admin/entrance-exam
```

---

## 5. Структура admin-web (Vue)

```
src/
  main.js, App.vue
  axios/axios.js                 как в user-web (Bearer-токен)
  router/router.js               маршруты + гард (требует role=admin)
  stores/
    admin.js                     токен, текущий админ
    ui.js                        тема
  services/
    auth.js
    stats.js                     дашборд
    moderation.js                жалобы + заявки
    teachers.js
    students.js
    materials.js
    exams.js
  components/
    layout/
      AdminLayout.vue            sidebar + topbar + <slot>
      Sidebar.vue                боковое меню (8 разделов)
    common/
      DataTable.vue              переиспользуемая таблица (поиск/сортировка)
      StatCard.vue               карточка метрики дашборда
      Modal.vue
      SearchInput.vue
    charts/
      BarChart.vue               распределение учеников по уровням
    moderation/
      ReportRow.vue
      ApplicationRow.vue
    exams/
      QuestionEditor.vue         конструктор вопросов
  pages/
    auth/login.vue
    dashboard.vue                /
    moderation.vue               /moderation (подвкладки)
    posts.vue                    /posts
    teachers.vue                 /teachers
    teacher-detail.vue           /teachers/:id
    students.vue                 /students
    materials.vue                /materials
    exams.vue                    /exams
    exam-edit.vue                /exams/new, /exams/:id
```

---

## 6. Структура admin-api (бэкенд, слои)

```
routers/admin/
  router.py                  агрегатор
  moderation.py              ✅ есть (заявки) + жалобы
  stats.py                   дашборд + статистика постов/учеников
  teachers.py
  students.py
  materials.py
  exams.py
db/repositories/
  report.py, material.py, exam.py, lesson_rating.py   (новые)
services/
  admin_stats.py             агрегации для дашборда/учеников
  moderation.py              расширить (жалобы, бан, варн)
  material.py, exam.py       CRUD-логика
core/deps.py
  + require_admin            гард + get_*_service для админских сервисов
```

> Общие модели (`Material`, `Exam`, `Report`, `LessonRating`, `User`) уже есть в
> `db/models`. Материалы/экзамены, созданные здесь, потребляет user-фронт
> (`GET /api/materials`, `GET /api/exams/level/{level}`, `GET /api/entrance-exam`).

---

## 7. Порядок сборки
1. **Гард + дашборд** — `require_admin`, `GET /api/admin/stats`, `AdminLayout` + Sidebar (каркас).
2. **Модерация** — заявки (уже частично) + жалобы + бан/варн. Сразу замыкает онбординг ролей.
3. **Материалы** + **Экзамены** — их тут же начинает потреблять обучение на user-фронте.
4. **Ученики** (график распределения) и **Преподаватели** (рейтинги/отзывы) — аналитика.
5. **Посты** — статистика (часть с заглушкой).

Первого админа: `UPDATE users SET role='admin' WHERE email='твой@email';`
