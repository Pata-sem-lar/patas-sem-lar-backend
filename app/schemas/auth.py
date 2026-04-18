from pydantic import BaseModel, EmailStr, field_validator

from app.models.usuario import RoleEnum
from app.schemas.usuario import UsuarioPublic


class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: RoleEnum
    telefone: str | None = None
    accepted_terms: bool

    @field_validator("senha")
    @classmethod
    def senha_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres")
        return v

    @field_validator("accepted_terms")
    @classmethod
    def must_accept_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Você deve aceitar os termos de uso")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioPublic
