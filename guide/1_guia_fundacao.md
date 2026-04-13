# Foundation Guide — Backend Phase 1

This guide explains what was built in Phase 1, why each piece exists, and how they connect to each other. Written for someone reading this code for the first time.

---

## The big picture

Before writing any feature, we built the foundation: a way to read configuration, a way to connect to the database, the definition of every table, and the migration system that creates those tables in PostgreSQL.

Nothing else works without these in place. A route can't query the database if there's no connection. Alembic can't create tables if it doesn't know the models exist. The models can't be registered if there's no `Base`.

This is the order everything was built — and the order matters:

```
1. .env + core/config.py     → app knows its settings
2. db/session.py             → app can connect to the database
3. models/mixins.py          → shared columns defined once
4. models/*.py               → all 6 tables defined
5. db/base.py                → Alembic can see all tables
6. alembic/env.py            → Alembic configured for async
7. alembic revision + upgrade → tables created in PostgreSQL
```

The folder structure inside `backend/`:

```
backend/
├── alembic/
│   ├── versions/            # generated migration files live here
│   └── env.py               # Alembic configuration
├── alembic.ini              # Alembic settings file
├── app/
│   ├── core/
│   │   └── config.py        # reads .env, exposes settings
│   ├── db/
│   │   ├── session.py       # database engine + session factory
│   │   └── base.py          # imports all models for Alembic
│   └── models/
│       ├── mixins.py        # shared Base, id, timestamps
│       ├── usuario.py
│       ├── loja.py
│       ├── profissional.py
│       ├── servico.py
│       ├── horario_trabalho.py
│       └── agendamento.py
├── compose.yml              # PostgreSQL in Docker
└── .env                     # secrets — never committed
```

---

## Docker + PostgreSQL

**Files:** `compose.yml`, `scripts/init-db.sql`

**Why Docker:** Avoids installing PostgreSQL directly on your machine. The database runs in a container — isolated, reproducible, and easy to reset. Everyone on the team runs the same version without configuring anything locally.

**compose.yml** defines the database container:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: agendei
      POSTGRES_PASSWORD: agendei
      POSTGRES_DB: agendei_dev
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agendei -d agendei_dev"]
      interval: 10s
      timeout: 5s
      retries: 5
```

`POSTGRES_DB` creates one database automatically. `init-db.sql` creates the second one (`agendei_test`) because Docker only auto-creates what's in `POSTGRES_DB`.

The `healthcheck` is important: it lets other services (like the API container) declare `depends_on: db: condition: service_healthy`, meaning they wait until Postgres is actually accepting connections — not just started.

`pgdata` is a named volume — data persists across container restarts. Without it, every `docker compose down` would wipe the database.

**Two databases:** `agendei_dev` for development, `agendei_test` for running tests. They're isolated so test runs don't pollute real data.

---

## `.env` + `core/config.py` — Configuration

**Why it exists:** The app needs values that change per environment — database address, JWT secret, etc. Hardcoding them is a security risk (secrets end up in git) and makes deployment impossible (dev and production point to different databases).

The solution: store values in `.env`, never commit it, and read it in one central place.

**`.env`** (gitignored):

```
DATABASE_URL=postgresql+asyncpg://agendei:agendei@localhost:5432/agendei_dev
DATABASE_URL_TEST=postgresql+asyncpg://agendei:agendei@localhost:5432/agendei_test
JWT_SECRET=change-me-before-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

**`.env.example`** is committed — it's a template teammates copy and fill in. No real secrets, just the keys.

**`config.py`:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    database_url_test: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_expiration_minutes: int

settings = Settings()  # type: ignore[call-arg]
```

`BaseSettings` reads the `.env` file and maps each key to a typed field. `DATABASE_URL` → `settings.database_url`. Case insensitive. If a required variable is missing, it raises an error immediately on startup — you find out right away instead of getting a cryptic error later when the variable is first used.

`settings` is created once at module load time. Every other file imports it:

```python
from app.core.config import settings

engine = create_async_engine(settings.database_url)
```

**Decision — `SettingsConfigDict` instead of inner `class Config`:** The inner `class Config` style is Pydantic v1 legacy syntax. `SettingsConfigDict` is the v2 way. Functionally equivalent, but v2 style is forward-compatible and gets better IDE support.

**Used by:** `db/session.py`, and later `core/security.py` for JWT.

---

## `db/session.py` — Database Connection

**Why it exists:** Models describe the tables, but something has to actually open a connection to PostgreSQL and run the queries. That's this file.

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
```

**Engine** — the connection pool. Think of it as the pipeline to the database. Created once when the app starts, shared for its entire lifetime. `echo=True` prints every SQL query to the terminal — useful in development, turn it off in production.

**Why `asyncpg`:** The database URL uses `postgresql+asyncpg://`. `asyncpg` is the async PostgreSQL driver. Without it, every database query would block the entire server while waiting for a response — in an async app that handles concurrent requests, that would be a serious performance problem.

**SessionLocal** — a factory that creates sessions. A session is one unit of work: open it, run your queries, commit or rollback, close it. One request = one session.

`expire_on_commit=False` — by default SQLAlchemy marks all loaded objects as "expired" after a commit, meaning the next time you access their attributes it tries to reload them from the database. In async code this causes an error because SQLAlchemy can't do a lazy synchronous query. Setting this to `False` keeps the objects valid after commit.

**`get_db()`** — a FastAPI dependency. The `yield` makes it a generator:

```python
async def get_db():
    async with SessionLocal() as session:
        yield session          # ← pauses here, gives session to the route
    # ← resumes here after the route finishes, session closes automatically
```

Routes use it via `Depends`:

```python
@router.get("/lojas")
async def list_lojas(db: AsyncSession = Depends(get_db)):
    # db is ready to use
    result = await db.execute(select(Loja))
    ...
```

FastAPI handles calling `get_db`, injecting the session, and closing it after the response. You never manage sessions manually in routes.

**Used by:** Every router that queries the database, via FastAPI's dependency injection system.

---

## `models/mixins.py` — Shared Columns

**Why it exists:** Every table needs an `id`, most need timestamps, and all use soft delete. Copy-pasting these columns into 6 model files would be repetitive and error-prone — changing the `id` type would mean editing 6 files. Mixins solve this with inheritance.

### `Base`

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

The parent class all models inherit from. SQLAlchemy uses it to track every registered table via `Base.metadata`. There must be exactly one `Base` in the entire app — if you accidentally create two, some models will be invisible to Alembic. It lives here so every model imports from this one place.

### `ULIDMixin`

```python
class ULIDMixin:
    id: Mapped[str] = mapped_column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )
```

Adds an `id` primary key to any model that inherits it. Generated in Python using the `python-ulid` library, stored as a 26-character string in PostgreSQL.

**Why ULID instead of UUID or integer:**

- **Integer IDs** are sequential — `/usuarios/1`, `/usuarios/2` exposes how many users you have and makes IDs guessable. A bad actor can enumerate records.
- **UUIDs** are random, not guessable, but have no ordering — you can't tell which was created first.
- **ULIDs** are random but time-sortable — the first 10 characters encode millisecond-precision timestamp, so sorting by `id` gives you chronological order. Best of both worlds.

### `TimestampMixin`

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
```

**`server_default=func.now()`** — the database sets the timestamp, not Python. If you used `default=datetime.now()` in Python, the timestamp would depend on the app server's clock. If multiple servers are running (horizontal scaling) and their clocks are slightly out of sync, you'd get inconsistent timestamps. The database clock is a single source of truth.

**`onupdate`** on `updated_at` — SQLAlchemy calls this lambda automatically whenever a row is updated. You never set `updated_at` manually.

**`deleted_at` and soft delete** — we never run `DELETE` in this app. When a record is "deleted", we set `deleted_at` to the current time and filter it out in queries with `.where(Model.deleted_at.is_(None))`. Reasons:

- Audit trail: you can see what was deleted and when
- Relational integrity: related records don't break
- GDPR: we need to distinguish between "soft deleted" and "anonymized" — two different things

**Used by:** All 6 model files.

---

## The 6 Models

### How to read a model

```python
class Loja(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "lojas"                          # PostgreSQL table name

    nome: Mapped[str] = mapped_column(String(100))   # NOT NULL, max 100 chars
    descricao: Mapped[Optional[str]] = mapped_column(Text)  # nullable
    owner_id: Mapped[str] = mapped_column(           # foreign key column
        String(26), ForeignKey("usuarios.id")
    )

    owner: Mapped[Usuario] = relationship("Usuario") # navigation, not a column
```

`Mapped[str]` = NOT NULL. `Mapped[Optional[str]]` = nullable. SQLAlchemy infers nullability from the Python type — you rarely write `nullable=True/False` explicitly.

`ForeignKey` references the **table name** (`"usuarios.id"`), not the Python class name. `relationship` is separate — it's not a database column, it's a Python-only convenience that lets you do `loja.owner` to get the `Usuario` object instead of just the `owner_id` string.

---

### `usuario.py` — the central table

Almost everything links back to `Usuario`. It holds both authentication data (`email`, `senha_hash`) and identity data (`nome`, `telefone`, `role`).

**`role`** is an Enum stored as a string in PostgreSQL:

```python
class RoleEnum(str, enum.Enum):
    cliente = "cliente"
    profissional = "profissional"
    admin_loja = "admin_loja"
```

Inheriting from `str` means values serialize as plain strings in JSON — `"cliente"` instead of `{"value": "cliente"}`. This role controls what each user can access — enforced in `core/dependencies.py` via `require_role()`.

**GDPR fields:**

- `accepted_terms_at` + `accepted_terms_version` — records when and which version of terms a user accepted. Legal requirement.
- `anonymized_at` — records when personal data was wiped. The row stays (for relational integrity), but `nome`, `email`, `telefone` get replaced with anonymized values. This is the "right to be forgotten" under GDPR — not the same as soft delete.

---

### `loja.py` — store

`owner_id` FK links a store to its `admin_loja` user. Contact fields are mostly optional — a store can be created with just a name and completed later.

`is_active` is a separate flag from `deleted_at`. Soft delete removes it permanently; `is_active = false` hides it from public listings while keeping it manageable in the admin panel.

---

### `profissional.py` — professional

A join between `Usuario` and `Loja`. A user with role `profissional` also has a row here with extra attributes (`bio`, `foto_url`). These don't belong on `Usuario` because not all users are professionals.

Two FKs: `usuario_id` (who the person is) and `loja_id` (where they work). Both have `relationship()` for navigation.

---

### `servico.py` — service

Belongs to a `Profissional`, not a `Loja` directly. This is intentional — different professionals in the same store can offer different services at different prices.

`preco` uses `Numeric(10, 2)` — never `float` for money. Floating point can't represent most decimal numbers exactly: `0.1 + 0.2 = 0.30000000000000004`. A billing error from this would be embarrassing. `Numeric` stores the exact decimal value.

`duracao_minutos` is what the availability algorithm uses to determine how long a slot takes and when the next one can start.

---

### `horario_trabalho.py` — work schedule

One row per working day per professional. A professional who works Monday to Friday has 5 rows.

`dia_semana` is an integer 0–6 matching Python's `date.weekday()` (0 = Monday, 6 = Sunday). The availability algorithm does `data.weekday()` on the requested date and looks up the matching row.

No `TimestampMixin` — work schedules don't need audit columns. If a schedule changes, you update or deactivate rows, and `is_active` handles visibility.

---

### `agendamento.py` — appointment

The most connected table. Links `cliente_id` → `profissional_id` → `servico_id` with a time slot.

**`data_hora_fim` is stored, not calculated.** When creating an appointment, the service calculates `data_hora_inicio + servico.duracao_minutos` and stores the result. The availability algorithm queries overlapping appointments using both fields — if you recalculated on every query, you'd need a join to `servicos` on every availability check, which is slow.

**`status` flow:**

```
pendente → confirmado → concluido
    └──────────────────→ cancelado
```

Only `pendente` and `confirmado` block a slot. `cancelado` and `concluido` free it up.

**`cancelado_por`** is a plain `String(26)`, not a FK with `relationship`. We only need to record the ID of who cancelled — we don't need to navigate from an appointment to the canceller as an object. A relationship would add complexity for no practical benefit here.

**`lembrete_enviado`** prevents the reminder email job from sending duplicates. The job queries all appointments within the reminder window where `lembrete_enviado = false`, sends emails, and sets the flag to `true`.

**`foreign_keys=[cliente_id]` on the `cliente` relationship:** `Usuario` appears twice in this table — `cliente_id` and `cancelado_por` (which also stores a user ID). SQLAlchemy sees two paths to `Usuario` and doesn't know which one `cliente` should use. The `foreign_keys` hint removes the ambiguity.

---

## `db/base.py` — the Alembic bridge

```python
from app.models.mixins import Base        # noqa: F401
from app.models.usuario import Usuario    # noqa: F401
from app.models.loja import Loja          # noqa: F401
from app.models.profissional import Profissional  # noqa: F401
from app.models.servico import Servico    # noqa: F401
from app.models.horario_trabalho import HorarioTrabalho  # noqa: F401
from app.models.agendamento import Agendamento  # noqa: F401
```

Alembic scans `Base.metadata` to find tables. A model only registers with `Base` when its class is imported — Python doesn't auto-discover files. If you add a new model and forget to add it here, Alembic generates a migration with the table missing and you find out only when it's not in the database.

`# noqa: F401` silences the linter's "imported but unused" warning. The imports aren't unused — they're doing real work as a side effect of loading the class.

**Used by:** `alembic/env.py` only. Not imported anywhere at runtime.

---

## `alembic/` — Migrations

Migrations are version-controlled SQL scripts that evolve the database schema over time. Instead of manually running `CREATE TABLE` or `ALTER TABLE`, Alembic generates and runs them for you.

### `alembic.ini`

The settings file. Two lines that matter:

```ini
script_location = alembic   # where the migration files are
prepend_sys_path = .         # adds backend/ to Python path so "from app..." imports work
```

Everything else is Python logging configuration.

### `alembic/env.py`

Alembic's runtime configuration. The default is sync-only — we rewrote it to support async:

```python
from app.core.config import settings
from app.db.base import Base  # triggers all model imports

target_metadata = Base.metadata  # Alembic reads this to know what tables exist

async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.database_url, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)  # bridge: async → sync
```

`do_run_migrations` is a regular sync function passed to `run_sync()`. Alembic itself isn't async-native, so this is the pattern for using it with an async engine — run Alembic's sync code inside an async connection via `run_sync`.

`pool.NullPool` means no connection pooling during migrations — each migration command opens a fresh connection and closes it. Pooling is unnecessary for a one-shot script.

### The migration workflow

```bash
# Generate a migration by comparing models to the current database schema
uv run alembic revision --autogenerate -m "description"

# Apply all pending migrations
uv run alembic upgrade head

# Roll back one migration
uv run alembic downgrade -1

# See current migration status
uv run alembic current
```

`--autogenerate` reads `Base.metadata` (all your models) and compares it to the actual database schema. It generates the `CREATE TABLE` / `ALTER TABLE` SQL automatically. You should always review the generated file before running it.

The generated file goes into `alembic/versions/` with a hash prefix — for example `a1b2c3d4_initial.py`. Each file has an `upgrade()` and a `downgrade()` function so migrations are reversible.

---

## How it all connects

```
.env
 └── core/config.py          reads .env, exposes typed settings
      ├── db/session.py       uses DATABASE_URL → engine + get_db()
      └── alembic/env.py      uses DATABASE_URL → migration engine

models/mixins.py              defines Base, ULIDMixin, TimestampMixin
 └── all 6 model files        inherit from mixins, define table columns

db/base.py                    imports all models (side effect: registers them with Base)
 └── alembic/env.py           reads Base.metadata → knows all tables → generates migrations
```

**Request lifecycle:**

```
HTTP request arrives
 └── FastAPI router matches the route
      └── FastAPI calls get_db() via Depends
           └── session opens
                └── route calls a service function, passes session
                     └── service runs queries using session + model classes
                          └── response sent → session closes
```

The service layer is where business logic lives — not in the route and not in the model. Routes are thin: they receive a request, call a service, return a response. Services are testable in isolation because they receive a session as a parameter instead of creating one themselves.
