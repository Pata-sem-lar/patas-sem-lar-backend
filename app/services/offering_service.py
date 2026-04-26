from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offering import Offering
from app.models.user import User
from app.schemas.offering import OfferingCreate, OfferingUpdate
from app.services.professional_service import get_professional


async def _verify_owner(db: AsyncSession, professional_id: str, user: User) -> None:
    professional = await get_professional(db, professional_id)
    if professional.user_id != user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")


async def create_offering(
    db: AsyncSession,
    professional_id: str,
    data: OfferingCreate,
    user: User,
) -> Offering:
    await _verify_owner(db, professional_id, user)

    offering = Offering(
        professional_id=professional_id,
        name=data.name,
        description=data.description,
        price=data.price,
        duration_minutes=data.duration_minutes,
    )
    db.add(offering)
    await db.commit()
    await db.refresh(offering)
    return offering


async def list_professional_offerings(
    db: AsyncSession, professional_id: str
) -> list[Offering]:
    await get_professional(db, professional_id)
    result = await db.execute(
        select(Offering).where(
            Offering.professional_id == professional_id,
            Offering.deleted_at.is_(None),
            Offering.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def get_offering(db: AsyncSession, offering_id: str) -> Offering:
    result = await db.execute(
        select(Offering).where(
            Offering.id == offering_id,
            Offering.deleted_at.is_(None),
        )
    )
    offering = result.scalar_one_or_none()
    if offering is None:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return offering


async def update_offering(
    db: AsyncSession,
    offering_id: str,
    data: OfferingUpdate,
    user: User,
) -> Offering:
    offering = await get_offering(db, offering_id)
    await _verify_owner(db, offering.professional_id, user)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(offering, field, value)

    await db.commit()
    await db.refresh(offering)
    return offering


async def delete_offering(
    db: AsyncSession, offering_id: str, user: User
) -> None:
    offering = await get_offering(db, offering_id)
    await _verify_owner(db, offering.professional_id, user)

    offering.deleted_at = datetime.now(timezone.utc)
    await db.commit()
