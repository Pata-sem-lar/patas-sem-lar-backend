from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import Base, TimestampMixin, ULIDMixin
from app.models.usuario import Usuario


class Loja(Base, ULIDMixin, TimestampMixin):
    __tablename__ = "lojas"

    owner_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("usuarios.id"))
    nome: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    telefone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    endereco: Mapped[Optional[str]] = mapped_column(String(255))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    owner: Mapped[Usuario] = relationship("Usuario")
