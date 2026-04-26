# Backend Conventions

Stack: FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL + Pydantic v2 + python-ulid + python-jose

---

## Naming Conventions

- **Always in English** — Portuguese only in user-facing strings (HTTPException `detail`) and comments
- Existing files that use Portuguese names (e.g. `loja_service.py`, `criar_loja`) are grandfathered — do not rename them. Keep surrounding new code in English.
- Models: `PascalCase` → `Loja`, `HorarioTrabalho`
- Schemas: `PascalCase` with suffix → `LojaCreate`, `LojaUpdate`, `LojaPublic`
- Services: `snake_case` module + `snake_case` functions → `loja_service.py` / `criar_loja()`
- Routers: `snake_case` module → `loja.py`
- Enums: `PascalCase` class + `UPPER_SNAKE` or readable string values → `class RoleEnum(str, enum.Enum)`

---

## Model Shape

Reference: `app/models/loja.py`

```python
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import Base, TimestampMixin, ULIDMixin


class Loja(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "lojas"

    owner_id: Mapped[str] = mapped_column(String(26), ForeignKey("usuarios.id"))
    nome: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    owner: Mapped["Usuario"] = relationship("Usuario")
```

Rules:

- Always inherit `Base, ULIDMixin, TimestampMixin` in that order
- `ULIDMixin` generates `id` automatically — never set it manually
- `TimestampMixin` provides `created_at`, `updated_at`, `deleted_at` — never redefine them
- `updated_at` is updated automatically via `onupdate` — never set it in service code
- **Never hard-delete** — always soft delete via `deleted_at`
- All new models must be added to `app/db/base.py` or Alembic will skip them silently
- Money fields: `Numeric(10, 2)` — never `Float`
- Enums: inherit from `(str, enum.Enum)` so they serialize as plain strings in JSON

---

## Schema Shape

Reference: `app/schemas/usuario.py`

```python
from pydantic import BaseModel, ConfigDict


class LojaCreate(BaseModel):
    nome: str
    descricao: str | None = None


class LojaUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None


class LojaPublic(BaseModel):
    id: str
    nome: str
    descricao: str | None

    model_config = ConfigDict(from_attributes=True)
```

Rules:

- `*Create` — required fields explicit, optional fields default to `None`
- `*Update` — all fields optional; service uses `model_dump(exclude_unset=True)`
- `*Public` — response shape; always has `model_config = ConfigDict(from_attributes=True)`
- Never expose `deleted_at`, `senha_hash`, or internal fields in `*Public` schemas
- One schema file per domain entity

---

## Service Shape

Reference: `app/services/auth_service.py`

```python
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.loja import Loja
from app.models.usuario import Usuario
from app.schemas.loja import LojaCreate, LojaUpdate


async def get_loja(db: AsyncSession, loja_id: str) -> Loja:
    result = await db.execute(
        select(Loja).where(Loja.id == loja_id, Loja.deleted_at.is_(None))
    )
    loja = result.scalar_one_or_none()
    if loja is None:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return loja


async def deletar_loja(db: AsyncSession, loja_id: str, current_user: Usuario) -> None:
    loja = await get_loja(db, loja_id)
    if loja.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    loja.deleted_at = datetime.now(timezone.utc)
    await db.commit()
```

Rules:

- All functions `async`
- Business logic and authorization checks live in the service, not the router
- Soft delete: `deleted_at = datetime.now(timezone.utc)` — never `datetime.utcnow()` (deprecated)
- Always filter deleted records: `.where(Model.deleted_at.is_(None))`
- `db.commit()` then `db.refresh(obj)` when you need the updated object back
- Raise `HTTPException` directly from the service — no custom exception classes unless the project grows to need them
- One service file per domain entity

---

## Router Shape

Reference: `app/routers/auth.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.usuario import RoleEnum, Usuario
from app.schemas.loja import LojaCreate, LojaPublic
from app.services import loja_service

router = APIRouter(prefix="/lojas", tags=["lojas"])


@router.get("", response_model=list[LojaPublic])
async def listar_lojas(db: AsyncSession = Depends(get_db)):
    return await loja_service.listar_lojas(db)


@router.post("", response_model=LojaPublic, status_code=201)
async def criar_loja(
    dados: LojaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(RoleEnum.admin_loja)),
):
    return await loja_service.criar_loja(db, dados, current_user.id)
```

Rules:

- Public routes: only `Depends(get_db)`
- Protected routes: `Depends(require_role(...))` — already decodes JWT and checks role
- `require_role` returns the `Usuario` object — use it directly, no second `get_current_user` call
- Always set `response_model` and `status_code` explicitly
- DELETE endpoints return `status_code=204` with no body (return `None` or `Response()`)
- Router registers in `main.py` — never import routers from other routers

---

## Domain Rules

- `role = profissional` não pode ser criado via `POST /auth/register` — o registro público aceita apenas `cliente` e `admin_loja`
- Profissionais são criados exclusivamente via `POST /lojas/{id}/profissionais` pelo admin dono da loja, que cria atomicamente um `USUARIO` + `PROFISSIONAL` numa única transação
- O `RoleEnum` continua com os três valores no modelo — apenas o schema `PublicRoleEnum` em `schemas/auth.py` restringe o registro público

---

## Forbidden Patterns

| Pattern | Use instead |
| --- | --- |
| `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| Hard `DELETE` SQL | Soft delete via `deleted_at` |
| Manual `id = str(ULID())` in service | Let `ULIDMixin` generate it |
| Setting `updated_at` manually | Let SQLAlchemy `onupdate` handle it |
| `float` for money | `Numeric(10, 2)` |
| `from_orm()` (Pydantic v1) | `model_validate(obj)` |
| `.dict()` (Pydantic v1) | `.model_dump()` |
| Business logic in the router | Move to service |
| Auth checks in the router | Move to service (ownership checks) |
| `print()` left in code | Remove before committing |

---

## Import Order

1. Standard library (`datetime`, `typing`, `enum`)
2. Third-party (`fastapi`, `sqlalchemy`, `pydantic`, `jose`)
3. Internal — `app.core`, `app.db`, `app.models`, `app.schemas`, `app.services`

---

## Folder Rules

- `app/models/` — one file per entity; all models imported in `app/db/base.py`
- `app/schemas/` — one file per entity; only Pydantic, no SQLAlchemy imports
- `app/services/` — one file per entity; business logic, DB queries, HTTPException
- `app/routers/` — one file per entity; thin layer — validates input, calls service, returns response
- `app/core/` — `config.py`, `security.py`, `dependencies.py` — project-wide concerns only
- `app/db/` — `session.py` (engine + `get_db`), `base.py` (all model imports for Alembic)
- `tests/` — mirrors `app/` structure; one test file per router

---

## Tests

Reference: `tests/conftest.py`, `tests/auth/test_auth.py`

### Setup

- `asyncio_mode = "auto"` is set in `pyproject.toml` — async test functions need no decorator
- Tests hit a **real PostgreSQL database** (`database_url_test`) — never mock the DB or use SQLite
- `reset_database` fixture (autouse) drops and recreates all tables before each test — full isolation
- `db_session` uses a savepoint + rollback so the DB is clean without recreating tables on every test
- `client` overrides `get_db` with the test session — HTTP request and DB assertions share the same transaction

### Structure

- `tests/` mirrors `app/routers/` — one subfolder per router: `tests/auth/`, `tests/loja/`, etc.
- Each subfolder has `__init__.py` and one `test_<router>.py`
- `conftest.py` at `tests/` root — shared fixtures only (`reset_database`, `db_session`, `client`)

### Test file shape

```python
from httpx import AsyncClient

BASE_URL = "/api/v1/lojas"

VALID_LOJA = {"nome": "Salão da Ana"}  # minimal valid payload as module constant


# ---------------------------------------------------------------------------
# POST /lojas
# ---------------------------------------------------------------------------


async def test_criar_loja_success(client: AsyncClient):
    # setup — create prerequisite state via HTTP (not direct DB inserts)
    response = await client.post(BASE_URL, json=VALID_LOJA, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    body = response.json()
    assert body["nome"] == VALID_LOJA["nome"]
    assert "id" in body
    assert "deleted_at" not in body


async def test_criar_loja_unauthorized(client: AsyncClient):
    response = await client.post(BASE_URL, json=VALID_LOJA)
    assert response.status_code == 401
```

Rules:

- Group tests by endpoint with a separator comment (`# ---... GET /lojas ...---`)
- Name tests as `test_<action>_<scenario>` — `test_criar_loja_success`, `test_criar_loja_unauthorized`
- Use module-level constants for URLs and valid payloads — never hardcode strings inside test bodies
- Build state via HTTP requests (register + login), not by inserting directly into `db_session`
- Always assert status code first, then body fields
- Cover at minimum: happy path, unauthenticated (401), wrong role (403), not found (404)
- Never assert exact error message strings — assert status code only for error cases (messages can change)

---

## Migrations (Alembic)

- Never edit the database schema directly — always generate a migration
- After adding or changing a model: `alembic revision --autogenerate -m "description"`
- Review the generated file before applying — autogenerate is not always correct
- Apply: `alembic upgrade head`
- All new models must be imported in `app/db/base.py` before generating migrations
