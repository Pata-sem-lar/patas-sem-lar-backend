from pydantic import BaseModel, ConfigDict

from app.models.user import RoleEnum


class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)
