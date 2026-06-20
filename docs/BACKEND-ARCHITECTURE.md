# Бэкенд — слои (конвенция)

Каждый домен раскладывается на 3 слоя + тонкий роутер. Правило: **зависимости
идут только вниз** (router → service → repository → model). Верхний слой не лезет
в чужие обязанности.

```
app/db/models/<domain>.py         ORM-модель (таблица)
app/db/repositories/<domain>.py   доступ к данным: ТОЛЬКО запросы к БД
app/services/<domain>.py          класс-сервис: бизнес-логика, держит репозиторий
app/routers/<user|admin>/<x>.py   эндпоинты: парсят запрос, зовут сервис, отдают ответ
```

## Кто за что отвечает

| Слой | Можно | Нельзя |
|---|---|---|
| **Repository** | SQL-запросы, CRUD | бизнес-правила, HTTP |
| **Service** | проверки, расчёты, оркестрация репозиториев | прямой SQL, знать про Request/Response |
| **Router** | валидация (Pydantic), DI, коды ответов | бизнес-логику, обращения к БД |

## Эталон — домен `auth`

- `db/repositories/base.py` — `BaseRepository[Model]` (get/add)
- `db/repositories/user.py` — `UserRepository(get_by_email, create, ...)`
- `services/auth.py` — `AuthService(db)` держит `UserRepository`, методы
  `register / login / authenticate`
- `core/deps.py` — `get_auth_service(db)` собирает сервис; роутер получает его через
  `Depends`
- `routers/user/auth.py` — три эндпоинта по 1–2 строки

## Как добавить новый домен (пример: posts)

1. `db/models/post.py` — модель (уже есть)
2. `db/repositories/post.py`:
   ```python
   class PostRepository(BaseRepository[Post]):
       model = Post
       def feed(self, limit, cursor): ...
   ```
3. `services/post.py`:
   ```python
   class PostService:
       def __init__(self, db): self.posts = PostRepository(db)
       def create(self, author_id, text): ...  # тут модерация языка и т.п.
   ```
4. `core/deps.py`: `def get_post_service(db=Depends(get_db)): return PostService(db)`
5. `routers/user/posts.py`: эндпоинты зовут `service`, подключить в `routers/user/router.py`
