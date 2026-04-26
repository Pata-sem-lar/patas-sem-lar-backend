from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.professional import Professional
from app.models.user import User, RoleEnum
from app.schemas.professional import ProfessionalCreate, ProfessionalSelfCreate, ProfessionalUpdate
from app.services.store_service import get_store


async def add_professional(
    db: AsyncSession,
    store_id: str,
    data: ProfessionalCreate,
    admin: User,
) -> Professional:
    store = await get_store(db, store_id)

    if store.owner_id != admin.id:
        raise HTTPException(status_code=403, detail="Apenas o dono da loja pode adicionar profissionais")

    existing = await db.execute(
        select(User).where(User.email == data.email, User.deleted_at.is_(None))
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=RoleEnum.professional,
    )
    db.add(user)
    await db.flush()

    professional = Professional(
        user_id=user.id,
        store_id=store_id,
        bio=data.bio,
        photo_url=data.photo_url,
    )
    db.add(professional)
    await db.commit()
    await db.refresh(professional)
    return professional


async def add_admin_as_professional(
    db: AsyncSession,
    store_id: str,
    data: ProfessionalSelfCreate,
    admin: User,
) -> Professional:
    store = await get_store(db, store_id)

    if store.owner_id != admin.id:
        raise HTTPException(status_code=403, detail="Apenas o dono da loja pode se vincular como profissional")

    existing = await db.execute(
        select(Professional).where(
            Professional.user_id == admin.id,
            Professional.store_id == store_id,
            Professional.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Você já é profissional desta loja")

    professional = Professional(
        user_id=admin.id,
        store_id=store_id,
        bio=data.bio,
        photo_url=data.photo_url,
    )
    db.add(professional)
    await db.commit()
    await db.refresh(professional)
    return professional


async def list_store_professionals(
    db: AsyncSession, store_id: str
) -> list[Professional]:
    await get_store(db, store_id)
    result = await db.execute(
        select(Professional).where(
            Professional.store_id == store_id,
            Professional.deleted_at.is_(None),
            Professional.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def get_professional(db: AsyncSession, professional_id: str) -> Professional:
    result = await db.execute(
        select(Professional).where(
            Professional.id == professional_id,
            Professional.deleted_at.is_(None),
        )
    )
    professional = result.scalar_one_or_none()
    if professional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    return professional


async def update_professional(
    db: AsyncSession,
    professional_id: str,
    data: ProfessionalUpdate,
    admin: User,
) -> Professional:
    professional = await get_professional(db, professional_id)
    store = await get_store(db, professional.store_id)

    if store.owner_id != admin.id:
        raise HTTPException(status_code=403, detail="Apenas o dono da loja pode editar profissionais")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(professional, field, value)

    await db.commit()
    await db.refresh(professional)
    return professional


async def remove_professional(
    db: AsyncSession, professional_id: str, admin: User
) -> None:
    professional = await get_professional(db, professional_id)
    store = await get_store(db, professional.store_id)

    if store.owner_id != admin.id:
        raise HTTPException(status_code=403, detail="Apenas o dono da loja pode remover profissionais")

    professional.deleted_at = datetime.now(timezone.utc)
    await db.commit()
