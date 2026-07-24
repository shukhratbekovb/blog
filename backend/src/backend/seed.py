import asyncio

from sqlalchemy import delete

from backend.core.database import SessionFactory, engine
from backend.core.security import hash_password
from backend.models import Base, User, Category, Tag, Post, post_tags


USERS = [
    {
        "username": "alice_dev",
        "email": "alice@example.com",
        "password": "password123",
        "bio": "Full-stack developer passionate about Python and React.",
        "karma": 120,
        "is_superuser": True,
    },
    {
        "username": "bob_writes",
        "email": "bob@example.com",
        "password": "password123",
        "bio": "Tech blogger and open-source contributor.",
        "karma": 85,
    },
    {
        "username": "carol_codes",
        "email": "carol@example.com",
        "password": "password123",
        "bio": "Backend engineer. Loves databases and clean architecture.",
        "karma": 60,
    },
    {
        "username": "dan_learns",
        "email": "dan@example.com",
        "password": "password123",
        "bio": "Junior developer on the journey from zero to hero.",
        "karma": 15,
    },
]

CATEGORIES = [
    {"name": "Python", "slug": "python", "description": "Everything about Python programming language."},
    {"name": "Web Development", "slug": "web-development", "description": "Frontend, backend, and full-stack web topics."},
    {"name": "DevOps", "slug": "devops", "description": "CI/CD, containers, cloud infrastructure and automation."},
    {"name": "Databases", "slug": "databases", "description": "SQL, NoSQL, ORMs and data modeling."},
    {"name": "Career", "slug": "career", "description": "Tips for growing your tech career."},
]

TAGS = [
    {"name": "FastAPI", "slug": "fastapi"},
    {"name": "SQLAlchemy", "slug": "sqlalchemy"},
    {"name": "Docker", "slug": "docker"},
    {"name": "PostgreSQL", "slug": "postgresql"},
    {"name": "React", "slug": "react"},
    {"name": "TypeScript", "slug": "typescript"},
    {"name": "Python", "slug": "python-tag"},
    {"name": "REST API", "slug": "rest-api"},
    {"name": "Async", "slug": "async"},
    {"name": "Tutorial", "slug": "tutorial"},
]

POSTS = [
    {
        "title": "Getting Started with FastAPI",
        "slug": "getting-started-with-fastapi",
        "content": (
            "FastAPI is a modern, fast web framework for building APIs with Python 3.8+ based on standard Python type hints. "
            "In this post we will walk through setting up a minimal FastAPI application, adding path operations, and running "
            "the development server. FastAPI automatically generates interactive docs via Swagger UI and ReDoc.\n\n"
            "## Installation\n\n```bash\npip install fastapi uvicorn\n```\n\n"
            "## Hello World\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n"
            "@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}\n```\n\n"
            "Run it with `uvicorn main:app --reload` and visit http://127.0.0.1:8000/docs."
        ),
        "category": "python",
        "tags": ["fastapi", "python-tag", "rest-api", "tutorial"],
        "author": "alice_dev",
        "is_published": True,
        "views_count": 342,
        "votes": 28,
    },
    {
        "title": "SQLAlchemy 2.0 — What's New",
        "slug": "sqlalchemy-2-0-whats-new",
        "content": (
            "SQLAlchemy 2.0 introduced a completely revamped Core and ORM API. The biggest change is the new 2.0-style "
            "query interface that replaces the legacy `Query` object. Mapped classes now use `Mapped[]` annotations for "
            "cleaner, type-safe column definitions.\n\n"
            "## Mapped columns example\n\n```python\nclass User(Base):\n    __tablename__ = 'users'\n"
            "    id: Mapped[int] = mapped_column(primary_key=True)\n"
            "    name: Mapped[str] = mapped_column(String(100))\n```"
        ),
        "category": "databases",
        "tags": ["sqlalchemy", "python-tag", "postgresql"],
        "author": "alice_dev",
        "is_published": True,
        "views_count": 215,
        "votes": 19,
    },
    {
        "title": "Async Python with asyncio",
        "slug": "async-python-with-asyncio",
        "content": (
            "Asynchronous programming allows a single thread to handle many tasks concurrently by yielding control while "
            "waiting for I/O. Python's `asyncio` module provides the event loop and coroutine support.\n\n"
            "```python\nimport asyncio\n\nasync def main():\n    await asyncio.sleep(1)\n    print('Done')\n\n"
            "asyncio.run(main())\n```\n\n"
            "When combined with async libraries like `aiohttp` or `asyncpg`, you can achieve very high throughput."
        ),
        "category": "python",
        "tags": ["async", "python-tag", "tutorial"],
        "author": "alice_dev",
        "is_published": True,
        "views_count": 178,
        "votes": 14,
    },
    {
        "title": "Docker for Python Developers",
        "slug": "docker-for-python-developers",
        "content": (
            "Containerising your Python application makes it reproducible and easy to deploy anywhere. "
            "A minimal `Dockerfile` for a FastAPI app looks like this:\n\n"
            "```dockerfile\nFROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\n"
            "RUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\"]\n```\n\n"
            "Use `docker-compose` to wire up your app with a PostgreSQL container for local development."
        ),
        "category": "devops",
        "tags": ["docker", "fastapi", "python-tag"],
        "author": "bob_writes",
        "is_published": True,
        "views_count": 289,
        "votes": 23,
    },
    {
        "title": "PostgreSQL Indexing Strategies",
        "slug": "postgresql-indexing-strategies",
        "content": (
            "Proper indexing is one of the highest-leverage ways to speed up your database queries. "
            "PostgreSQL supports B-tree (default), Hash, GIN, GiST, and BRIN indexes.\n\n"
            "- **B-tree**: great for equality and range queries on ordered data.\n"
            "- **GIN**: perfect for full-text search and JSONB columns.\n"
            "- **BRIN**: extremely compact index for naturally ordered large tables (e.g. timestamps).\n\n"
            "Always use `EXPLAIN ANALYZE` to verify that your index is actually being used."
        ),
        "category": "databases",
        "tags": ["postgresql", "sqlalchemy", "tutorial"],
        "author": "bob_writes",
        "is_published": True,
        "views_count": 198,
        "votes": 17,
    },
    {
        "title": "Building a REST API with FastAPI and SQLAlchemy",
        "slug": "building-rest-api-fastapi-sqlalchemy",
        "content": (
            "In this tutorial we build a fully functional blog REST API from scratch. "
            "We cover project structure, SQLAlchemy models, Alembic migrations, Pydantic schemas, "
            "dependency injection, and JWT authentication.\n\n"
            "The final project supports CRUD for posts, comments, tags, and categories — "
            "exactly what you'd need for a real-world application."
        ),
        "category": "web-development",
        "tags": ["fastapi", "sqlalchemy", "rest-api", "postgresql"],
        "author": "bob_writes",
        "is_published": True,
        "views_count": 512,
        "votes": 47,
    },
    {
        "title": "CI/CD Pipeline with GitHub Actions",
        "slug": "cicd-pipeline-with-github-actions",
        "content": (
            "GitHub Actions lets you automate your build, test, and deploy workflows directly from your repository. "
            "A typical Python workflow runs linting, tests, and then deploys to a cloud provider.\n\n"
            "```yaml\nname: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n"
            "        with:\n          python-version: '3.12'\n      - run: pip install pytest\n"
            "      - run: pytest\n```"
        ),
        "category": "devops",
        "tags": ["docker", "tutorial"],
        "author": "carol_codes",
        "is_published": True,
        "views_count": 143,
        "votes": 11,
    },
    {
        "title": "React + TypeScript: The Right Setup",
        "slug": "react-typescript-the-right-setup",
        "content": (
            "Starting a React project with TypeScript from scratch can be overwhelming. "
            "Vite is now the recommended build tool — it's blazing fast and has first-class TS support.\n\n"
            "```bash\nnpm create vite@latest my-app -- --template react-ts\ncd my-app && npm install && npm run dev\n```\n\n"
            "Add `eslint`, `prettier`, and `@typescript-eslint` for a solid developer experience."
        ),
        "category": "web-development",
        "tags": ["react", "typescript", "tutorial"],
        "author": "carol_codes",
        "is_published": True,
        "views_count": 267,
        "votes": 21,
    },
    {
        "title": "Understanding Database Transactions",
        "slug": "understanding-database-transactions",
        "content": (
            "ACID properties — Atomicity, Consistency, Isolation, Durability — are the foundation of reliable databases. "
            "A transaction groups multiple SQL statements into a single unit of work that either fully succeeds or fully rolls back.\n\n"
            "PostgreSQL supports all four isolation levels: Read Uncommitted, Read Committed (default), "
            "Repeatable Read, and Serializable."
        ),
        "category": "databases",
        "tags": ["postgresql", "sqlalchemy"],
        "author": "carol_codes",
        "is_published": True,
        "views_count": 189,
        "votes": 15,
    },
    {
        "title": "How I Landed My First Dev Job",
        "slug": "how-i-landed-my-first-dev-job",
        "content": (
            "After six months of self-study, open-source contributions, and a handful of rejected applications, "
            "I finally got an offer. Here's what made the difference:\n\n"
            "1. Build real projects (not just tutorials).\n"
            "2. Contribute to open source — even small fixes show up on your GitHub profile.\n"
            "3. Write about what you learn — blogging signals communication skills.\n"
            "4. Network in local meetups and online communities."
        ),
        "category": "career",
        "tags": ["tutorial"],
        "author": "dan_learns",
        "is_published": True,
        "views_count": 410,
        "votes": 38,
    },
    {
        "title": "Alembic Migrations Cheat Sheet",
        "slug": "alembic-migrations-cheat-sheet",
        "content": (
            "Alembic is the de-facto migration tool for SQLAlchemy projects. Quick reference:\n\n"
            "```bash\n# Create a new migration\nalembic revision --autogenerate -m 'add users table'\n\n"
            "# Apply all pending migrations\nalembic upgrade head\n\n"
            "# Roll back one step\nalembic downgrade -1\n\n"
            "# Show current revision\nalembic current\n```\n\n"
            "Always review autogenerated migrations before applying them in production."
        ),
        "category": "databases",
        "tags": ["sqlalchemy", "postgresql", "python-tag"],
        "author": "alice_dev",
        "is_published": True,
        "views_count": 322,
        "votes": 26,
    },
    {
        "title": "Kubernetes for the Impatient",
        "slug": "kubernetes-for-the-impatient",
        "content": (
            "Kubernetes (K8s) orchestrates containers across a cluster of machines. Core concepts:\n\n"
            "- **Pod**: smallest deployable unit, wraps one or more containers.\n"
            "- **Deployment**: manages ReplicaSets to keep a desired number of pods running.\n"
            "- **Service**: stable network endpoint for a set of pods.\n"
            "- **Ingress**: HTTP routing rules from the outside world into services.\n\n"
            "Start locally with `minikube` or `kind` before moving to a managed cluster."
        ),
        "category": "devops",
        "tags": ["docker", "tutorial"],
        "author": "bob_writes",
        "is_published": True,
        "views_count": 234,
        "votes": 19,
    },
    {
        "title": "TypeScript Generics Explained",
        "slug": "typescript-generics-explained",
        "content": (
            "Generics let you write reusable, type-safe code without sacrificing flexibility. "
            "Instead of `any`, use a type parameter:\n\n"
            "```typescript\nfunction identity<T>(value: T): T {\n  return value;\n}\n\n"
            "const num = identity<number>(42);   // T = number\nconst str = identity('hello');   // T inferred as string\n```\n\n"
            "Generics shine in data structures, API response wrappers, and utility types."
        ),
        "category": "web-development",
        "tags": ["typescript", "react"],
        "author": "carol_codes",
        "is_published": True,
        "views_count": 201,
        "votes": 16,
    },
    {
        "title": "Python Dependency Management with Poetry",
        "slug": "python-dependency-management-with-poetry",
        "content": (
            "Poetry replaces `pip` + `virtualenv` + `setup.py` with a single tool. "
            "It manages your virtual environment, locks dependencies, and can publish packages to PyPI.\n\n"
            "```bash\npoetry new my-project\npoetry add fastapi uvicorn\npoetry add --group dev pytest\npoetry run pytest\n```\n\n"
            "`pyproject.toml` becomes the single source of truth for your project metadata and dependencies."
        ),
        "category": "python",
        "tags": ["python-tag", "tutorial"],
        "author": "alice_dev",
        "is_published": True,
        "views_count": 276,
        "votes": 22,
    },
    {
        "title": "Redis as a Cache Layer",
        "slug": "redis-as-a-cache-layer",
        "content": (
            "Redis is an in-memory data store commonly used to cache expensive database queries or API responses. "
            "With `aioredis` you can integrate it into a FastAPI app:\n\n"
            "```python\nimport aioredis\n\nredis = aioredis.from_url('redis://localhost')\n\n"
            "async def get_cached(key: str):\n    cached = await redis.get(key)\n    return cached\n```\n\n"
            "Set a TTL with `await redis.setex(key, 300, value)` to auto-expire stale data."
        ),
        "category": "databases",
        "tags": ["fastapi", "async", "python-tag"],
        "author": "bob_writes",
        "is_published": True,
        "views_count": 187,
        "votes": 14,
    },
    {
        "title": "Writing Clean Python Code",
        "slug": "writing-clean-python-code",
        "content": (
            "Clean code is easy to read, reason about, and change. In Python, follow these principles:\n\n"
            "- Use meaningful names — `user_count` beats `n`.\n"
            "- Keep functions short and focused on one thing.\n"
            "- Prefer list comprehensions over loops when the intent is clear.\n"
            "- Use type hints everywhere — they are documentation that the type checker can verify.\n"
            "- Write tests first when fixing bugs so you can prove the bug is fixed."
        ),
        "category": "python",
        "tags": ["python-tag", "tutorial"],
        "author": "carol_codes",
        "is_published": True,
        "views_count": 310,
        "votes": 29,
    },
    {
        "title": "Frontend State Management in 2025",
        "slug": "frontend-state-management-in-2025",
        "content": (
            "State management has evolved significantly. The landscape today:\n\n"
            "- **Zustand**: minimal boilerplate, great for medium-sized apps.\n"
            "- **Jotai / Recoil**: atomic model, perfect for fine-grained reactivity.\n"
            "- **TanStack Query**: server state, caching, and background refetching out of the box.\n"
            "- **Redux Toolkit**: still solid for large teams that need predictable state.\n\n"
            "For most new projects, TanStack Query + Zustand covers 90% of use cases."
        ),
        "category": "web-development",
        "tags": ["react", "typescript"],
        "author": "dan_learns",
        "is_published": True,
        "views_count": 158,
        "votes": 12,
    },
    {
        "title": "Soft Skills Every Developer Needs",
        "slug": "soft-skills-every-developer-needs",
        "content": (
            "Technical skills get you the interview; soft skills get you the job and keep you growing.\n\n"
            "**Communication**: Write clear PR descriptions, ask precise questions, give useful code-review feedback.\n\n"
            "**Empathy**: Understand what the user actually needs, not just what they asked for.\n\n"
            "**Time management**: Break large tasks into small deliverables and communicate blockers early.\n\n"
            "**Continuous learning**: The tech landscape changes fast — schedule learning time every week."
        ),
        "category": "career",
        "tags": ["tutorial"],
        "author": "dan_learns",
        "is_published": True,
        "views_count": 295,
        "votes": 31,
    },
    {
        "title": "Monitoring FastAPI with Prometheus and Grafana",
        "slug": "monitoring-fastapi-with-prometheus-and-grafana",
        "content": (
            "Observability is essential in production. Add `prometheus-fastapi-instrumentator` to expose "
            "request duration, count, and error rate metrics automatically.\n\n"
            "```python\nfrom prometheus_fastapi_instrumentator import Instrumentator\n\n"
            "Instrumentator().instrument(app).expose(app)\n```\n\n"
            "Scrape metrics with Prometheus, visualise them in Grafana, and set up alerts so you know before users do."
        ),
        "category": "devops",
        "tags": ["fastapi", "docker", "async"],
        "author": "alice_dev",
        "is_published": False,
        "views_count": 0,
        "votes": 0,
    },
    {
        "title": "My Learning Roadmap for 2025",
        "slug": "my-learning-roadmap-2025",
        "content": (
            "This year I'm focusing on three areas:\n\n"
            "1. **Systems programming** — learning Rust to understand memory management without a GC.\n"
            "2. **Cloud architecture** — AWS Solutions Architect Associate certification.\n"
            "3. **Data engineering** — Apache Kafka and dbt for building reliable data pipelines.\n\n"
            "I'll document my progress here on the blog. If you're on a similar path, let's connect!"
        ),
        "category": "career",
        "tags": ["tutorial"],
        "author": "dan_learns",
        "is_published": True,
        "views_count": 88,
        "votes": 7,
    },
]


async def clear_data(session):
    await session.execute(delete(post_tags))
    for model in (Post, Tag, Category, User):
        await session.execute(delete(model))
    await session.commit()


async def seed():
    async with SessionFactory() as session:
        await clear_data(session)

        # --- Users ---
        user_map: dict[str, User] = {}
        for u in USERS:
            user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                bio=u.get("bio"),
                karma=u.get("karma", 0),
                is_active=True,
                is_superuser=u.get("is_superuser", False),
            )
            session.add(user)
            user_map[u["username"]] = user

        await session.flush()

        # --- Categories ---
        category_map: dict[str, Category] = {}
        for c in CATEGORIES:
            category = Category(
                name=c["name"],
                slug=c["slug"],
                description=c.get("description"),
            )
            session.add(category)
            category_map[c["slug"]] = category

        await session.flush()

        # --- Tags ---
        tag_map: dict[str, Tag] = {}
        for t in TAGS:
            tag = Tag(name=t["name"], slug=t["slug"])
            session.add(tag)
            tag_map[t["slug"]] = tag

        await session.flush()

        # --- Posts ---
        for p in POSTS:
            post = Post(
                title=p["title"],
                slug=p["slug"],
                content=p["content"],
                author_id=user_map[p["author"]].id,
                category_id=category_map[p["category"]].id,
                is_published=p.get("is_published", True),
                views_count=p.get("views_count", 0),
                votes=p.get("votes", 0),
                tags=[tag_map[slug] for slug in p.get("tags", [])],
            )
            session.add(post)

        # Update posts_count on each tag
        tag_usage: dict[str, int] = {}
        for p in POSTS:
            for slug in p.get("tags", []):
                tag_usage[slug] = tag_usage.get(slug, 0) + 1
        for slug, count in tag_usage.items():
            tag_map[slug].posts_count = count

        await session.commit()
        print(f"Seeded {len(USERS)} users, {len(CATEGORIES)} categories, {len(TAGS)} tags, {len(POSTS)} posts.")


if __name__ == "__main__":
    asyncio.run(seed())
