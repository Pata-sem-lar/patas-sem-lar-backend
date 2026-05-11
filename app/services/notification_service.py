from typing import Sequence
from datetime import datetime, UTC
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationPublic,
    NotificationUpdateStatus,
)

# CREATE
async def create_notification(
        db: AsyncSession,
        data: NotificationCreate,
) -> NotificationPublic:
    notification = Notification(**data.model_dump())
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return NotificationPublic.model_validate(notification)


# GET BY ID (ORM — uso interno)
async def _get_notification_orm(db: AsyncSession, notification_id: str) -> Notification:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.deleted_at.is_(None),
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


# GET BY ID
async def get_notification(
        db: AsyncSession,
        notification_id: str,
) -> NotificationPublic:
    notification = await _get_notification_orm(db, notification_id)
    return NotificationPublic.model_validate(notification)


# LIST
async def list_notifications(
        db: AsyncSession,
        *,
        status: str | None = None,
        recipient_id: str | None = None,
        recipient_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
) -> Sequence[NotificationPublic]:
    query = select(Notification).where(Notification.deleted_at.is_(None))

    if status:
        query = query.where(Notification.status == status)

    if recipient_id:
        query = query.where(Notification.recipient_id == recipient_id)

    if recipient_type:
        query = query.where(Notification.recipient_type == recipient_type)

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    notifications = result.scalars().all()

    return [
        NotificationPublic.model_validate(n)
        for n in notifications
    ]


# UPDATE STATUS (worker)
async def update_status(
        db: AsyncSession,
        notification_id: str,
        data: NotificationUpdateStatus,
) -> NotificationPublic:
    notification = await _get_notification_orm(db, notification_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)

    await db.commit()
    await db.refresh(notification)

    return NotificationPublic.model_validate(notification)


async def get_pending_notifications(
        db: AsyncSession,
        limit: int = 50,
) -> list[NotificationPublic]:
    query = (
        select(Notification)
        .where(
            Notification.status == "pending",
            Notification.scheduled_at <= datetime.now(UTC),
            Notification.deleted_at.is_(None),
        )
        .limit(limit)
    )

    result = await db.execute(query)
    return [NotificationPublic.model_validate(n) for n in result.scalars().all()]
