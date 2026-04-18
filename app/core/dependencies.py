from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.db.session import get_db
from app.models.usuario import RoleEnum, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = security.decode_token(token)
    except JWTError:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise credentials_exception

    result = await db.execute(
        select(Usuario).where(
            Usuario.id == user_id,
            Usuario.deleted_at.is_(None),
        )
    )
    usuario = result.scalar_one_or_none()
    if usuario is None:
        raise credentials_exception

    return usuario


def require_role(*roles: RoleEnum):
    def role_checker(
        current_user: Usuario = Depends(get_current_user),
    ) -> Usuario:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return current_user

    return role_checker
