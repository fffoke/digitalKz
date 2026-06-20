# ТІЛДЕС — Фронтенд (user-web): структура файлов + endpoints

PWA на **Vue 3 + Vite + Pinia + vue-router + Tailwind + vite-plugin-pwa**
(всё уже стоит). 5 вкладок снизу как на макете + «Сөз дня» в ленте + Дуэли.

---

## 1. Навигация (нижнее меню — 5 вкладок)

| Вкладка | Маршрут | Экран |
|---|---|---|
| 🏠 Дом | `/` | Лента + карточка «Сөз дня» |
| ✉️ Директ | `/messages` | Сообщения |
| 📖 Обучение | `/learn` | Выбор роли / дашборд ученика / препода |
| 🔔 Активность | `/activity` | Уведомления |
| 👤 Профиль | `/profile` | Профиль |

Доп. экраны: `/login` `/register` `/verify` `/teacher/apply` `/onboarding/test`
`/post/:id` `/duels` `/duels/:id` `/messages/:id` `/groups/find` `/groups/create`
`/groups/:id` `/homework/:id` `/exam/:level` `/u/:username` `/profile/edit`.

---

## 2. Структура файлов

```
src/
  main.js
  App.vue
  axios/axios.js                 (есть) базовый axios + Bearer-токен
  router/
    router.js                    (есть) маршруты + гарды (auth/guest)
  assets/main.css                (есть)

  stores/                        Pinia
    user.js                      (есть) профиль, токен, роль
    ui.js                        тема (тёмная/светлая — иконка солнца на макете)
    feed.js                      лента, лайки, репосты
    wordOfDay.js                 слово/тема дня
    duel.js                      дуэли, очередь, результат
    learning.js                  дашборд ученика, группа, план, прогресс
    teacher.js                   дашборд преподавателя
    messages.js                  диалоги, чаты
    notifications.js             уведомления (+ роль одобрена = пуш)

  services/                      обёртки над API (по доменам)
    auth.js                      (есть)
    onboarding.js                role-status, verification, teacher/apply
    posts.js                     лента, комменты, лайки, репост, жалобы
    wordOfDay.js                 слово дня
    duels.js                     дуэли
    learning.js                  дашборд/группа/прогресс/ДЗ/экзамены
    groups.js                    поиск/создание/вступление в группу
    teacher.js                   группы, уроки, проверка ДЗ
    messages.js                  диалоги/сообщения
    users.js                     профили, подписки
    notifications.js             уведомления

  components/
    layout/
      AppLayout.vue              каркас: TopBar + <slot> + BottomNav
      BottomNav.vue              нижнее меню (5 вкладок)
      TopBar.vue                 заголовок + переключатель темы
    common/
      Avatar.vue
      Spinner.vue
      EmptyState.vue
      AppModal.vue
      VoiceRecorder.vue          ⭐ запись голоса (MediaRecorder) → отправка на whisper
                                   используется в тесте, экзамене и дуэлях
    auth/                        (есть) AuthLayout, AuthInput, AuthButton,
                                 RoleSwitcher, AppLogo
    feed/
      PostCard.vue               пост (лайк/коммент/репост/жалоба)
      PostComposer.vue           «Поделитесь чем-нибудь…» + публикация
      WordOfDayCard.vue          ⭐ «бүгінгі сөз: қамқорлық» + кнопка «Составить предложение»
      CommentItem.vue
    duel/
      DuelInviteCard.vue         ⭐ «Языковая дуэль» — найти соперника
      DuelArena.vue              ⭐ арена: фраза + таймер + VoiceRecorder
      DuelResult.vue             ⭐ вердикт ИИ-судьи (победитель, баллы, разбор)
      DuelLeaderboard.vue        таблица лидеров
    learning/
      RoleSelectCard.vue         «Стать учеником / преподавателем»
      StudentHeader.vue          уровень, ранг, прогресс, streak
      ProgressMap.vue            карта прогресса (узлы секций/этапов)
      GroupPlan.vue              план группы (секции → этапы ✓/текущий/🔒)
      ExamCountdown.vue          таймер до экзамена + «Подготовиться»
      GroupCard.vue              карточка группы (вступить)
      HomeworkCard.vue           текущее ДЗ
    teacher/
      TeacherStats.vue           проведено уроков / ученики / рейтинг
      AvailableGroupCard.vue     группа без преподавателя → «Взять группу»
      LessonRow.vue              ближайший урок (открыть/отменить)
      ReviewItem.vue             отзыв ученика
    profile/
      ProfileHeader.vue          аватар, био, подписчики/подписки
      ProfileTabs.vue            Посты / Ответы / Репосты
    notifications/
      NotificationItem.vue
    messages/
      DialogItem.vue
      ChatBubble.vue

  pages/
    landing.vue                  (есть)
    auth/
      login.vue                  (есть)
      register.vue               (есть)
      verify.vue                 (есть) верификация ученика
      verify-pending.vue         (есть)
      teacher-apply.vue          анкета преподавателя
    feed/
      home.vue                   🏠 лента + WordOfDayCard
      post.vue                   /post/:id — пост + комментарии
    duels/
      duels.vue                  /duels — лобби, лидерборд, «найти соперника»
      duel.vue                   /duels/:id — арена + результат
    messages/
      messages.vue               ✉️ список диалогов
      chat.vue                   /messages/:id
    learn/
      learn.vue                  📖 роутер по роли (user→выбор, student/teacher→дашборд)
      student-dashboard.vue      дашборд ученика (как на десктоп-макете)
      teacher-dashboard.vue      дашборд преподавателя
      find-groups.vue            /groups/find
      create-group.vue           /groups/create
      group.vue                  /groups/:id (план, карта, чат, ДЗ)
      homework.vue               /homework/:id
      exam.vue                   /exam/:level
      entrance-test.vue          /onboarding/test (вступительный тест)
    activity/
      activity.vue               🔔 уведомления (Все / Подписки / Упоминания)
    profile/
      profile.vue                👤 /profile и /u/:username
      edit-profile.vue           /profile/edit
```

---

## 3. Карта маршрутов (router.js)

| Path | Page | Гард |
|---|---|---|
| `/` | feed/home | auth |
| `/post/:id` | feed/post | auth |
| `/duels` | duels/duels | auth |
| `/duels/:id` | duels/duel | auth |
| `/messages` | messages/messages | auth |
| `/messages/:id` | messages/chat | auth |
| `/learn` | learn/learn | auth |
| `/groups/find` | learn/find-groups | auth |
| `/groups/create` | learn/create-group | auth |
| `/groups/:id` | learn/group | auth |
| `/homework/:id` | learn/homework | auth |
| `/exam/:level` | learn/exam | auth |
| `/onboarding/test` | learn/entrance-test | auth |
| `/activity` | activity/activity | auth |
| `/profile` `/u/:username` | profile/profile | auth |
| `/profile/edit` | profile/edit-profile | auth |
| `/teacher/apply` | auth/teacher-apply | auth |
| `/verify` `/verify-pending` | auth/* | auth |
| `/landing` `/login` `/register` | * | guest |

`AppLayout` (TopBar + BottomNav) оборачивает все `auth`-страницы; на
`landing/login/register` — без нижнего меню.

---

## 4. ⭐ Новые фичи

### 4.1 «Сөз дня» / тема дня
- На **Доме** сверху — `WordOfDayCard`: сегодняшнее слово + перевод + призыв
  «Составь предложение». Клик → `PostComposer` с предзаполненным тегом слова.
- Пост, созданный по слову дня, помечается и попадает в подборку дня.

**Endpoints**
```
GET  /api/word-of-day                # { date, word, translation, theme, prompt }
GET  /api/word-of-day/posts          # лента постов по сегодняшнему слову
GET  /api/word-of-day/leaderboard    # топ авторов по лайкам за слово дня
POST /api/posts                      # { text, word_of_day_id? } — обычная публикация
```

### 4.2 Языковые дуэли 1v1
- `/duels`: лидерборд + кнопка «Найти соперника» (матчмейкинг по уровню).
- `/duels/:id` (`DuelArena`): обоим даётся фраза/вопрос → каждый отвечает
  **голосом** (`VoiceRecorder`) → whisper расшифровывает → ИИ-судья сравнивает
  и выбирает победителя (`DuelResult`: баллы + разбор).

**Endpoints**
```
GET  /api/duels                      # мои/активные дуэли
POST /api/duels/queue                # встать в очередь → matchmaking → { duel_id, opponent, prompt }
GET  /api/duels/{id}                 # состояние { prompt, status, players, your_turn }
POST /api/duels/{id}/answer          # multipart audio → whisper (services/transcription.py)
GET  /api/duels/{id}/result          # { winner, scores, feedback } — вердикт LLM
GET  /api/duels/leaderboard          # таблица лидеров
```

---

## 5. Полный список endpoints (что дёргает фронт)

```
# AUTH / ONBOARDING                          (бэк готов)
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
GET    /api/me/role-status
POST   /api/verification
POST   /api/teacher/apply
GET    /api/notifications

# ЛЕНТА / СӨЗ ДНЯ
GET    /api/posts
POST   /api/posts
GET    /api/posts/{id}
DELETE /api/posts/{id}
POST   /api/posts/{id}/like
DELETE /api/posts/{id}/like
POST   /api/posts/{id}/repost
POST   /api/posts/{id}/report
GET    /api/posts/{id}/comments
POST   /api/posts/{id}/comments
GET    /api/word-of-day
GET    /api/word-of-day/posts
GET    /api/word-of-day/leaderboard

# ДУЭЛИ
GET    /api/duels
POST   /api/duels/queue
GET    /api/duels/{id}
POST   /api/duels/{id}/answer
GET    /api/duels/{id}/result
GET    /api/duels/leaderboard

# ДИРЕКТ
GET    /api/conversations
POST   /api/conversations
GET    /api/conversations/{id}/messages
POST   /api/conversations/{id}/messages

# ОБУЧЕНИЕ (ученик)
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
GET    /api/entrance-exam
POST   /api/entrance-exam/submit
GET    /api/exams/level/{level}
POST   /api/exams/{id}/submit
POST   /api/lessons/{id}/rate
GET    /api/materials?level=A2

# ОБУЧЕНИЕ (преподаватель)
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

# ПРОФИЛЬ / СОЦИАЛКА
GET    /api/users/{username}
GET    /api/users/{username}/posts
GET    /api/users/{username}/replies
GET    /api/users/{username}/reposts
POST   /api/users/{id}/follow
DELETE /api/users/{id}/follow
GET    /api/users/{id}/followers
GET    /api/users/{id}/following
PATCH  /api/profile
```

---

## 6. PWA

`vite-plugin-pwa` уже настроен (manifest TILDES, autoUpdate). Что доделать:
- иконки `public/pwa-192.png` и `public/pwa-512.png` (в манифесте уже прописаны);
- офлайн-кэш статики (workbox по умолчанию);
- позже — Web Push для пуша о выдаче роли / ходе дуэли (пока MVP опрашивает
  `GET /api/notifications`).

---

## 7. Порядок сборки (рекомендация)
1. `AppLayout` + `BottomNav` + `TopBar` + тема (`ui.js`) — каркас под все вкладки.
2. **Дом**: `PostCard`, `PostComposer`, `WordOfDayCard` + `feed.js` (демо-наглядность).
3. **Профиль** + **Активность** (быстро, на тех же данных).
4. **Обучение**: выбор роли → дашборд ученика → группа → ДЗ → экзамен.
5. **Дуэли**: `VoiceRecorder` → арена → результат (вау-фича).
6. **Директ** — последним.
```
