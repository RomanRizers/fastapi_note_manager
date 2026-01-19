# Note Manager на FastAPI

Приложение для создания, просмотра и удаления заметок.
## Описание проекта

Это учебное веб-приложение на FastAPI с серверными шаблонами (Jinja2) и базой SQLite.
Интерфейс позволяет добавлять и удалять заметки. Данные хранятся локально.

## Стек технологий

- Python 3.13+
- FastAPI
- SQLAlchemy 2.x
- Jinja2
- SQLite
- Uvicorn

## Основные возможности

- Создание заметок через HTML-форму
- Просмотр списка заметок
- Удаление заметок с подтверждением
- Серверный рендеринг HTML

## Теория и структура FastAPI проекта

FastAPI — современный веб-фреймворк на Python, ориентированный на типизацию и
быстрое создание API и веб-приложений. В нашем проекте он используется вместе с
SQLAlchemy и Jinja2, что дает понятное разделение ответственности:

1) **Модели (models)** — описание структуры данных.
2) **Схемы (schemas)** — входные/выходные данные и валидация (Pydantic).
3) **CRUD (crud)** — функции, которые изолируют работу с базой.
4) **Приложение (main)** — маршруты и связывание слоев.
5) **Шаблоны (templates)** — HTML-рендеринг.
6) **Статика (static)** — CSS и JS.

Этот репозиторий — учебный проект менеджера заметок на FastAPI + SQLAlchemy + Jinja2.
Ниже — подробная пошаговая инструкция: как поднять решение, как оно устроено внутри,
и как воспроизвести проект с нуля, включая ключевые фрагменты кода с объяснениями.

## 1. Как запустить проект

### Вариант А — локально (рекомендуемый для разработки)

1) Убедитесь, что установлен Python.
   - `pyproject.toml` требует `>= 3.13`.
2) Установите зависимости:
   - через `uv`:
     ```bash
     uv sync --no-dev
     ```
   - или через `pip`:
     ```bash
     pip install -r <(python -m piptools compile pyproject.toml)
     ```
     Если у вас нет `piptools`, установите его:
     ```bash
     pip install piptools
     ```
3) Запустите приложение:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   Или без `uv`:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
4) Откройте в браузере:
   - `http://127.0.0.1:8000`

Примечание: SQLite база `notes.db` создается автоматически при первом старте.

### Вариант Б — Docker

1) Соберите и запустите контейнер:
   ```bash
   docker compose up --build
   ```
2) Откройте в браузере:
   - `http://127.0.0.1:8000`

## 2. Как устроен проект

### Структура

```
app/
  main.py            # Роуты FastAPI + запуск
  db.py              # Подключение к SQLite и сессии
  models.py          # SQLAlchemy модели
  schemas.py         # Pydantic схемы
  crud.py            # Функции доступа к данным
  templates/
    index.html       # HTML шаблон (Jinja2)
  static/
    style.css        # Стили
    app.js           # Логика интерфейса (подтверждение удаления)
Dockerfile
docker-compose.yml
pyproject.toml
notes.db             # База данных (локально)
```

### Главные компоненты

- **FastAPI** — веб-слой и маршруты.
- **Jinja2** — серверный рендеринг HTML.
- **SQLAlchemy** — работа с БД.
- **SQLite** — база данных в файле `notes.db`.

## 3. Методичка: как построить этот проект с нуля

Ниже пошагово разобрано, что и зачем делается. Эта часть — подробная инструкция,
чтобы вы могли воспроизвести проект самостоятельно.

### Шаг 1. Подготовка окружения и зависимостей

Создайте папку проекта и опишите зависимости в `pyproject.toml`:

```toml
[project]
name = "fastapi-note-manager"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
  "fastapi>=0.128.0",
  "jinja2>=3.1.6",
  "pydantic>=2.12.5",
  "python-multipart>=0.0.21",
  "sqlalchemy>=2.0.45",
  "uvicorn>=0.40.0",
]
```

Обратите внимание на `python-multipart` — он нужен для обработки HTML-форм.

### Шаг 2. Подключение базы данных (SQLite + SQLAlchemy)

Файл `app/db.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./notes.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

Что здесь важно:
- `sqlite:///./notes.db` — база хранится рядом с проектом.
- `check_same_thread=False` — позволяет использовать SQLite в асинхронном сервере.
- `Base = declarative_base()` — базовый класс для всех моделей.

### Шаг 3. Модель данных

Файл `app/models.py`:

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .db import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

Логика:
- `title` — обязательный заголовок.
- `content` — текст заметки.
- `created_at` — время создания по умолчанию.

### Шаг 4. Схемы Pydantic (валидация)

Файл `app/schemas.py`:

```python
from pydantic import BaseModel
from datetime import datetime

class NoteIn(BaseModel):
    title: str
    content: str | None = None

class NoteOut(NoteIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

Назначение:
- `NoteIn` — входные данные от формы.
- `NoteOut` — удобная модель для чтения из БД.

### Шаг 5. CRUD-операции

Файл `app/crud.py`:

```python
from sqlalchemy.orm import Session
from .models import Note
from .schemas import NoteIn

def get_notes(db: Session):
    return db.query(Note).all()

def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

def create_note(db: Session, note: NoteIn):
    obj = Note(**note.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_note(db: Session, note_id: int):
    note = get_note(db, note_id)
    if note:
        db.delete(note)
        db.commit()
    return note
```

Ключевая идея:
- Весь доступ к БД вынесен в отдельные функции.
- Это упрощает тестирование и поддержку.

### Шаг 6. Веб-приложение (FastAPI)

Файл `app/main.py`:

```python
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from .db import Base, engine, SessionLocal
from . import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Note Manager")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    notes = crud.get_notes(db)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "notes": notes}
    )

@app.post("/")
def add_note(
    title: str = Form(...),
    content: str = Form(""),
    db: Session = Depends(get_db),
):
    crud.create_note(db, schemas.NoteIn(title=title, content=content))
    return RedirectResponse("/", status_code=303)

@app.post("/delete/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    crud.delete_note(db, note_id)
    return RedirectResponse("/", status_code=303)
```

Пояснения:
- `Base.metadata.create_all(...)` создает таблицы при старте.
- `get_db()` — зависимость для работы с SQLAlchemy-сессией.
- `/` обрабатывает и выдачу списка заметок, и создание.
- `/delete/{note_id}` удаляет заметку и возвращает на главную.

### Шаг 7. HTML-шаблон

Файл `app/templates/index.html`:

```html
<form class="note-form" method="post">
  <input name="title" placeholder="Заголовок" required>
  <textarea name="content" placeholder="Текст заметки"></textarea>
  <button type="submit">Добавить</button>
</form>

<div class="notes">
  {% for note in notes %}
    <div class="note">
      <div class="note-header">
        <h3>{{ note.title }}</h3>
        <form method="post" action="/delete/{{ note.id }}">
          <button class="delete-btn">✕</button>
        </form>
      </div>
      <p>{{ note.content }}</p>
      <span class="date">
        {{ note.created_at.strftime("%d.%m.%Y %H:%M") }}
      </span>
    </div>
  {% else %}
    <p class="empty">Заметок пока нет</p>
  {% endfor %}
</div>
```

Что происходит:
- Сверху форма добавления.
- Ниже список заметок (или сообщение, что список пуст).
- Удаление — отдельная форма на каждую заметку.

### Шаг 8. Стили и JS

Файл `app/static/style.css` — задает внешний вид карточек, формы и кнопок.

Файл `app/static/app.js`:

```javascript
document.addEventListener("DOMContentLoaded", () => {
  const deletes = document.querySelectorAll(".delete-btn");
  deletes.forEach(btn => {
    btn.addEventListener("click", (e) => {
      if (!confirm("Удалить заметку?")) {
        e.preventDefault();
      }
    });
  });
});
```

Это добавляет подтверждение удаления, чтобы пользователь случайно не удалил заметку.

### Шаг 9. Docker-конфигурация

`Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install uv \
    && uv sync --no-dev
COPY app ./app
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`docker-compose.yml`:

```yaml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```

Пояснение:
- Контейнер поднимает веб-сервер.
- `volumes` позволяет видеть изменения кода без пересборки.

## 4. Точки расширения

Если хотите развивать проект:

- Добавить редактирование заметок (`/edit/{id}`).
- Подключить полноценный REST API (JSON вместо HTML).
- Вынести стили в отдельный дизайн-токены.
- Подключить PostgreSQL вместо SQLite.

## 5. Проверка работоспособности

Минимальный чек-лист:

1) Открывается главная страница.
2) Добавление заметки сохраняет её в список.
3) Удаление показывает подтверждение.
4) После удаления заметка исчезает.

Готово. Это полностью рабочий минимальный менеджер заметок на FastAPI.
