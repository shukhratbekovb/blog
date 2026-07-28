# DevTalks

**A technical blogging & community platform API** — write articles, organize them by category and tags, discuss in threaded comments, vote on posts, and bookmark what you want to read later.

Built with FastAPI on an async stack (PostgreSQL + Redis), containerized with Docker Compose.

> **Current version: `0.1.0`** — early-stage / pre-release. Core CRUD, auth, voting, and bookmarking are implemented; see [Roadmap](#roadmap) for what's still in progress.

![Version](https://img.shields.io/badge/version-0.1.0-blueviolet)
![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)
![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-migrations-4B8BBE)
![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis 7](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-dependency%20management-60A5FA?logo=poetry&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-auth-000000?logo=jsonwebtokens&logoColor=white)
![MIT License](https://img.shields.io/badge/license-MIT-green)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Run with Docker Compose](#run-with-docker-compose-recommended)
  - [Run locally with Poetry](#run-locally-with-poetry)
- [Environment Variables](#environment-variables)
- [Data Model](#data-model)
- [Authentication](#authentication)
- [API Reference](#api-reference)
- [Development](#development)
- [Roadmap](#roadmap)
- [License](#license)

---

## Features

- 📝 **Posts** — create, edit, publish/unpublish, delete; slugged URLs, view counter, filtering & pagination
- 🗂️ **Categories & Tags** — organize posts by category (one-to-many) and tags (many-to-many)
- 💬 **Threaded comments** — nested replies via self-referencing `parent_id`
- 👍 **Voting** — upvote/remove vote on posts, one vote per user (DB-enforced unique constraint)
- 🔖 **Bookmarks** — save posts to read later, per-user bookmark list
- 👤 **User profiles** — public profile, karma score, "my posts", "my bookmarks"
- 🔐 **JWT authentication** — access + refresh tokens, Argon2 password hashing, role-based access (superuser)
- ⚡ **Redis caching layer** — cache service scaffolded for hot read paths
- 🗃️ **Alembic migrations** — versioned schema, applied automatically by a dedicated `migrate` container on startup
- 🌱 **Seed script** — one command populates the DB with realistic demo users, categories, tags, and posts
- 🐳 **Fully dockerized** — `db`, `redis`, `migrate`, and `backend` services wired together with health checks

## Tech Stack

| Layer               | Technology                                                        |
|----------------------|--------------------------------------------------------------------|
| Language             | Python 3.13                                                        |
| Web framework        | FastAPI (async)                                                     |
| ASGI server          | Uvicorn                                                             |
| ORM                  | SQLAlchemy 2.0 (async, `Mapped[]` style)                            |
| Database             | PostgreSQL 16 (via `asyncpg`, `psycopg2-binary` for Alembic)        |
| Migrations           | Alembic                                                             |
| Cache                | Redis 7 (`redis[asyncio]`)                                          |
| Validation / schemas | Pydantic v2 + `pydantic-settings`                                   |
| Auth                 | `python-jose` (JWT), `passlib` + `argon2-cffi` (password hashing)  |
| Dependency management| Poetry                                                              |
| Containerization     | Docker, Docker Compose                                              |
| Slug generation      | `transliterate`                                                     |

## Project Structure

```
blog/
├── docker-compose.yml          # db, redis, migrate, backend services
└── backend/
    ├── Dockerfile
    ├── Makefile                 # dev, migrate shortcuts
    ├── pyproject.toml           # Poetry deps
    ├── alembic.ini
    ├── migrations/               # Alembic migration scripts
    └── src/backend/
        ├── main.py               # FastAPI app & router registration
        ├── core/
        │   ├── config.py         # Settings (env-driven)
        │   ├── database.py       # Async engine/session factory
        │   ├── security.py       # JWT + Argon2 password hashing
        │   └── cache.py          # Redis client & CacheService
        ├── api/v1/               # Route handlers (one router per resource)
        │   ├── auth.py
        │   ├── user.py
        │   ├── posts.py
        │   ├── category.py
        │   ├── tags.py
        │   ├── comments.py
        │   └── feed.py
        ├── dependencies/         # FastAPI Depends() wiring per resource
        ├── models/                # SQLAlchemy ORM models
        ├── repository/            # DB access layer (per-model repositories)
        ├── services/               # Business logic layer
        ├── schemas/                # Pydantic request/response models
        ├── utils/                  # slug generation, comment tree builder
        └── seed.py                 # Demo data seeding script
```

**Layering**: `api` (HTTP layer) → `services` (business logic) → `repository` (DB queries) → `models` (ORM). Dependencies are wired per-resource under `dependencies/` and injected via FastAPI's `Depends`.

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended path), **or**
- Python 3.13, [Poetry](https://python-poetry.org/), a local PostgreSQL 16 and Redis 7 instance

### Run with Docker Compose (recommended)

1. Create a `.env` file in the project root (see [Environment Variables](#environment-variables)).
2. Start everything:

   ```bash
   docker compose up --build
   ```

   This brings up, in order:
   - `db` — PostgreSQL 16, waits for a healthy `pg_isready`
   - `redis` — Redis 7
   - `migrate` — runs `alembic upgrade head` once, then exits
   - `backend` — FastAPI app on port `8000`, starts only after migrations succeed

3. Open the interactive API docs:
   - Swagger UI → http://localhost:8000/docs
   - ReDoc → http://localhost:8000/redoc
   - Health check → http://localhost:8000/health

### Run locally with Poetry

```bash
cd backend
poetry install

# create backend/.env (see below), pointing at your local Postgres/Redis

poetry run alembic upgrade head    # or: make migrate
poetry run uvicorn backend.main:app --reload --app-dir src   # or: make dev
```

Optionally seed demo data:

```bash
poetry run python -m backend.seed
```

## Environment Variables

The **root** `.env` configures Docker Compose (Postgres container credentials + backend config); the **backend** `.env` (`backend/.env`, or `BASE_DIR/.env` when run locally) configures the app directly. Neither file is committed — copy the example below and fill in your own secrets.

| Variable                        | Description                                                     | Example                                                    |
|----------------------------------|-------------------------------------------------------------------|-------------------------------------------------------------|
| `POSTGRES_USER`                  | Postgres superuser (Compose only)                                  | `postgres`                                                   |
| `POSTGRES_PASSWORD`              | Postgres password (Compose only)                                   | `change-me`                                                  |
| `POSTGRES_DB`                    | Database name (Compose only)                                       | `devtalks`                                                   |
| `DATABASE_URL`                   | Async SQLAlchemy connection string                                  | `postgresql+asyncpg://postgres:change-me@db:5432/devtalks`  |
| `REDIS_URL`                      | Redis connection string                                             | `redis://redis:6379`                                        |
| `SECRET_KEY`                     | Secret used to sign JWTs — **must be a strong, private value**     | `openssl rand -hex 32`                                       |
| `ALGORITHM`                      | JWT signing algorithm                                              | `HS256`                                                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES`    | Access token lifetime                                               | `30`                                                          |
| `REFRESH_TOKEN_EXPIRE_DAYS`      | Refresh token lifetime                                              | `30`                                                          |
| `DEBUG`                          | Debug flag                                                          | `true` / `false`                                             |

> ⚠️ Never commit real secrets. Rotate `SECRET_KEY` and database credentials before deploying anywhere beyond local development.

## Data Model

| Entity      | Key fields                                                        | Relationships                                                        |
|-------------|---------------------------------------------------------------------|-------------------------------------------------------------------------|
| `User`      | `username`, `email`, `hashed_password`, `bio`, `karma`, `is_superuser`| has many `Post`, `PostVote`, `Bookmark`                                 |
| `Post`      | `title`, `slug`, `content`, `is_published`, `views_count`, `votes`  | belongs to `User` (author) & `Category`; many-to-many `Tag`; has many `Comment`, `PostVote`, `Bookmark` |
| `Category`  | `name`, `slug`, `description`                                       | has many `Post`                                                        |
| `Tag`       | `name`, `slug`, `posts_count`                                       | many-to-many `Post` (via `post_tags`)                                  |
| `Comment`   | `content`, `votes_count`, `parent_id`                                | belongs to `User` & `Post`; self-referencing tree via `parent`/`replies` |
| `PostVote`  | unique (`user_id`, `post_id`)                                        | belongs to `User` & `Post`                                              |
| `Bookmark`  | `user_id`, `post_id`                                                 | belongs to `User` & `Post`                                              |

All models share an auto-increment `id` (`IdentityMixin`); most also share `created_at`/`updated_at` (`TimeStampMixin`) and a unique `slug` (`SlugMixin`).

## Authentication

- **Registration/login** issue an **access token** (short-lived, default 30 min) and a **refresh token** (long-lived, default 30 days), both signed HS256 JWTs carrying `sub` (user id) and `type` (`access`/`refresh`).
- Passwords are hashed with **Argon2** (`passlib` + `argon2-cffi`), never stored in plaintext.
- Protected endpoints expect `Authorization: Bearer <access_token>`.
- `POST /api/v1/auth/refresh` exchanges a valid refresh token for a new access token.
- `verify_superuser` dependency gates admin-only actions (e.g. deleting categories/tags).

## API Reference

Base path: `/api/v1`. Full interactive docs are always available at `/docs`.

#### Auth — `/auth`
| Method | Path                | Description                          | Auth |
|--------|---------------------|---------------------------------------|------|
| POST   | `/register`          | Register a new user                    | –    |
| POST   | `/login`             | Log in, get access + refresh tokens    | –    |
| POST   | `/refresh`           | Exchange refresh token for new access token | –  |
| POST   | `/change-password`   | Change current user's password         | ✅   |

#### Users — `/users`
| Method | Path                  | Description                          | Auth |
|--------|-----------------------|-----------------------------------------|------|
| GET    | `/`                    | List users (paginated)                  | –    |
| GET    | `/me`                  | Current user's profile                  | ✅   |
| PATCH  | `/me`                  | Update current user's profile           | ✅   |
| GET    | `/me/bookmarks`        | Current user's bookmarked posts         | ✅   |
| GET    | `/{user_id}`           | Public profile by id                    | –    |
| GET    | `/{user_id}/posts`     | Posts authored by a user                | –    |

#### Posts — `/posts`
| Method | Path                     | Description                       | Auth |
|--------|--------------------------|--------------------------------------|------|
| POST   | `/`                       | Create a post                        | ✅   |
| GET    | `/`                       | List posts (filters + pagination)    | –    |
| GET    | `/{slug}`                 | Get post by slug                     | –    |
| PATCH  | `/{post_id}`              | Update a post                        | ✅   |
| DELETE | `/{post_id}`              | Delete a post                        | ✅   |
| PATCH  | `/{post_id}/publish`      | Publish/unpublish a post              | ✅   |
| POST   | `/{post_id}/vote`         | Upvote a post                        | ✅   |
| DELETE | `/{post_id}/vote`         | Remove vote                          | ✅   |
| POST   | `/{post_id}/bookmark`     | Bookmark a post                      | ✅   |
| DELETE | `/{post_id}/bookmark`     | Remove bookmark                      | ✅   |

#### Comments — `/posts/{post_id}/comments`
| Method | Path              | Description                            | Auth |
|--------|-------------------|-------------------------------------------|------|
| GET    | `/`                | List comments for a post (threaded)       | –    |
| POST   | `/`                | Add a comment or reply                    | ✅   |
| GET    | `/{comment_id}`    | Get a single comment                      | –    |
| PUT    | `/{comment_id}`    | Update a comment                          | ✅   |
| DELETE | `/{comment_id}`    | Delete a comment                          | ✅   |

#### Categories — `/categories`
| Method | Path                  | Description             | Auth        |
|--------|-----------------------|----------------------------|--------------|
| POST   | `/`                    | Create a category           | ✅ superuser |
| GET    | `/`                    | List categories             | –            |
| GET    | `/{category_slug}`     | Get category by slug        | –            |
| PUT    | `/{category_id}`       | Update a category            | ✅ superuser |
| DELETE | `/{category_id}`       | Delete a category            | ✅ superuser |

#### Tags — `/tags`
| Method | Path         | Description       | Auth        |
|--------|--------------|----------------------|--------------|
| POST   | `/`           | Create a tag          | ✅           |
| GET    | `/`           | List tags (paginated) | –            |
| GET    | `/{tag_id}`   | Get tag by id          | –            |
| DELETE | `/{tag_id}`   | Delete a tag           | ✅ superuser |

#### Feed — `/feed`
| Method | Path              | Description                                        | Auth |
|--------|-------------------|-------------------------------------------------------|------|
| GET    | `/{feed_type}`     | Personalized feed — `new`, `top`, or `hot`             | –    |

> 🚧 The feed endpoint currently returns a stub response (`{"type": ..., "posts": []}`) — ranking logic isn't implemented yet, see [Roadmap](#roadmap).

## Development

```bash
cd backend

make dev                     # uvicorn --reload (local dev server)
make migrate                 # alembic upgrade head

poetry run alembic revision --autogenerate -m "message"   # create a new migration
poetry run python -m backend.seed                          # (re)seed demo data
```

The demo seed creates 4 users (one superuser), 5 categories, 10 tags, and ~19 posts with realistic content — handy for exploring the API without creating data by hand.

## Roadmap

- [ ] Implement real ranking logic for `/feed/{new,top,hot}` (currently a stub)
- [ ] Wire up `CacheService` (Redis) on hot read paths (post detail, feed, tag/category lists)
- [ ] Add automated test suite (`backend/tests` is currently scaffolded but empty)
- [ ] Rate limiting on auth endpoints

## License

Licensed under the [MIT License](LICENSE).
