# Проект для хакатона

## Стек

| Слой | Технологии |
|------|-----------|
| Frontend | React (Vite), Tailwind CSS, Axios |
| Backend | Python, Flask, SQLAlchemy, Flask-Migrate |
| БД | PostgreSQL |
| Инфраструктура | Docker, docker-compose |

## Структура проекта

```
project/
├── docker-compose.yml
├── .env.example
├── .env                  # не коммитить
├── .gitignore
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py           # точка входа
│   └── app/
│       ├── __init__.py   # create_app()
│       ├── config.py
│       ├── extensions.py # db, migrate, cors
│       ├── models/       # SQLAlchemy-модели
│       └── routes/       # Flask Blueprints
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── api/          # axios-клиент и функции запросов
        ├── components/
        ├── pages/
        ├── App.jsx
        └── main.jsx
```

Фронт и бек живут независимо, а в корне лежит всё, что связывает их вместе.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

После запуска:

- Фронтенд: http://localhost:5173
- Бекенд: http://localhost:5000/api/health
- PostgreSQL: localhost:5432

Остановка:

```bash
docker compose down        # остановить контейнеры
docker compose down -v     # остановить и удалить данные БД
```

## Миграции БД

Выполняются после того, как появились модели:

```bash
docker compose exec backend flask --app main db init      # один раз
docker compose exec backend flask --app main db migrate -m "init"
docker compose exec backend flask --app main db upgrade
```

> Модели нужно импортировать в `app/__init__.py` (или в `app/models/__init__.py`),
> иначе Flask-Migrate их не увидит.

## Запуск без Docker

Нужны установленные Python 3.12+, Node.js 22+ и PostgreSQL.

### 1. База данных

Вариант А: PostgreSQL установлен локально. Создайте пользователя и базу:

```bash
psql -U postgres -c "CREATE USER app WITH PASSWORD 'app';"
psql -U postgres -c "CREATE DATABASE app OWNER app;"
```

Вариант Б: поднять в Docker только БД, а бек и фронт запускать локально:

```bash
docker compose up db
```

### 2. Backend

```bash
cd backend

# создать виртуальное окружение
python -m venv venv

# активировать
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows (cmd / PowerShell)

# установить зависимости
pip install -r requirements.txt

# указать строку подключения к БД (хост localhost, а не db)
export DATABASE_URL=postgresql://app:app@localhost:5432/app          # Linux / macOS
set DATABASE_URL=postgresql://app:app@localhost:5432/app             # Windows cmd
$env:DATABASE_URL="postgresql://app:app@localhost:5432/app"          # Windows PowerShell

# применить миграции (если уже есть папка migrations)
flask --app main db upgrade

# запустить сервер
flask --app main run --debug
```

Бекенд будет доступен на http://localhost:5000/api/health.

Вместо `export` можно создать файл `backend/.env` со строкой `DATABASE_URL=...`. Flask подхватит его сам, а в git он не попадёт, потому что `.env` есть в `.gitignore`.

Если миграций ещё нет, инициализируйте их так:

```bash
flask --app main db init      # один раз
flask --app main db migrate -m "init"
flask --app main db upgrade
```

Чтобы выйти из виртуального окружения, выполните `deactivate`.

После установки новых библиотек обновляйте зависимости:

```bash
pip freeze > requirements.txt
```

### 3. Frontend

В новом терминале:

```bash
cd frontend
npm install
npm run dev
```

Фронтенд будет доступен на http://localhost:5173. Адрес API берётся из переменной `VITE_API_URL`. Если она не задана, используется `http://localhost:5000/api`, так что для локального запуска ничего настраивать не нужно.

Другие полезные команды:

```bash
npm run build      # продакшен-сборка в папку dist/
npm run preview    # локальный просмотр собранной версии
npm install <пакет>
```

---

## Создание проекта с нуля

Этот раздел нужен, если каркас ещё не создан.

### 1. Каркас

```bash
mkdir project && cd project
git init
mkdir -p backend/app/models backend/app/routes
touch backend/app/models/__init__.py backend/app/routes/__init__.py

# Frontend (Vite + React)
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install axios
npm install tailwindcss @tailwindcss/vite
cd ..
```

### 2. Frontend

**Tailwind (v4).** `frontend/vite.config.js`:

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { host: true, port: 5173, watch: { usePolling: true } },
})
```

В `frontend/src/index.css` оставить только одну строку:

```css
@import "tailwindcss";
```

**Axios-клиент** `frontend/src/api/client.js`:

```js
import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
})
```

### 3. Backend

`backend/requirements.txt`:

```
flask
flask-sqlalchemy
flask-migrate
flask-cors
psycopg2-binary
python-dotenv
gunicorn
```

`backend/app/extensions.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
```

`backend/app/config.py`:

```python
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

`backend/app/__init__.py`:

```python
from flask import Flask
from .config import Config
from .extensions import db, migrate, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from .routes.health import bp as health_bp
    app.register_blueprint(health_bp, url_prefix="/api")

    return app
```

`backend/app/routes/health.py`:

```python
from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)

@bp.get("/health")
def health():
    return jsonify(status="ok")
```

`backend/main.py`:

```python
from app import create_app

app = create_app()
```

### 4. Dockerfile'ы

`backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["flask", "--app", "main", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
```

`frontend/Dockerfile`:

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev"]
```

### 5. docker-compose.yml и .env

`.env.example`:

```
POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_DB=app
DATABASE_URL=postgresql://app:app@db:5432/app
VITE_API_URL=http://localhost:5000/api
```

`docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16-alpine
    env_file: .env
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build: ./backend
    env_file: .env
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build: ./frontend
    env_file: .env
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  pgdata:
```

`.gitignore` (минимум):

```
.env
node_modules/
__pycache__/
*.pyc
.venv/
```

---

## Советы для хакатона

- **Миграции.** Если времени мало, можно вместо них вызвать `db.create_all()` в `create_app()` внутри `with app.app_context():`. Но если модели у команды меняются, лучше сразу использовать Flask-Migrate. Тогда не придётся пересоздавать БД через `docker compose down -v`.
- **Git.** Договоритесь о ветках заранее (`main` плюс по ветке на человека или фичу) и закоммитьте каркас до того, как все начнут писать код. Это убережёт от конфликтов.
- **Контракт API.** В первый час зафиксируйте список эндпоинтов и формат JSON. Фронт тогда может работать на заглушках, пока бек не готов.
- **Продакшен-деплой.** Для демо dev-режима обычно достаточно. Если нужен прод, соберите фронт через `npm run build` и отдайте через nginx, а бек запустите через gunicorn (`gunicorn main:app`).
