from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store
from app.models.user import User
from app.schemas.store import StoreCreate, StoreUpdate


async def list_stores(db: AsyncSession) -> list[Store]:
    result = await db.execute(
        select(Store).where(
            Store.deleted_at.is_(None),
            Store.is_active.is_(True),
        )
    )
    return result.scalars().all()


async def list_my_stores(db: AsyncSession, owner_id: str) -> list[Store]:
    result = await db.execute(
        select(Store).where(
            Store.owner_id == owner_id,
            Store.deleted_at.is_(None),
            Store.is_active.is_(True),
        )
    )
    return result.scalars().all()


async def get_store(db: AsyncSession, store_id: str) -> Store:
    result = await db.execute(
        select(Store).where(Store.id == store_id, Store.deleted_at.is_(None))
    )
    store = result.scalar_one_or_none()
    if store is None:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return store


async def create_store(db: AsyncSession, data: StoreCreate, owner_id: str) -> Store:
    store = Store(**data.model_dump(), owner_id=owner_id)
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store


async def update_store(
    db: AsyncSession,
    store_id: str,
    data: StoreUpdate,
    current_user: User,
) -> Store:
    store = await get_store(db, store_id)
    if store.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(store, field, value)
    await db.commit()
    await db.refresh(store)
    return store


async def delete_store(
    db: AsyncSession,
    store_id: str,
    current_user: User,
) -> None:
    store = await get_store(db, store_id)
    if store.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    store.deleted_at = datetime.now(timezone.utc)
    await db.commit()
