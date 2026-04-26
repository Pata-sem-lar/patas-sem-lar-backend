from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.appointment import StatusEnum


class AppointmentCreate(BaseModel):
    """
    Client picks professional, offering, and start time.
    ends_at is calculated by the backend (starts_at + offering duration).
    """
    professional_id: str
    offering_id: str
    starts_at: datetime


class AppointmentUpdate(BaseModel):
    status: StatusEnum
    reason: str | None = None


class AppointmentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    professional_id: str
    offering_id: str
    starts_at: datetime
    ends_at: datetime
    status: StatusEnum
    cancelled_by: str | None
    cancellation_reason: str | None
    reminder_sent: bool


class AvailableSlot(BaseModel):
    start: datetime
    end: datetime
