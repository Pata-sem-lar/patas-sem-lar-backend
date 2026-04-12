from sqlalchemy import Boolean, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import Base, ULIDMixin
from app.models.profissional import Profissional


class HorarioTrabalho(Base, ULIDMixin):
    __tablename__ = "horarios_trabalho"

    profissional_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("profissionais.id"))
    dia_semana: Mapped[int] = mapped_column(Integer)  # 0=segunda ... 6=domingo
    hora_inicio: Mapped[str] = mapped_column(Time)
    hora_fim: Mapped[str] = mapped_column(Time)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    profissional: Mapped[Profissional] = relationship("Profissional")
