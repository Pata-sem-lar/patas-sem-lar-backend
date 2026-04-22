from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.servico import Servico
from app.models.usuario import Usuario
from app.schemas.servico import ServicoCreate, ServicoUpdate
from app.services.profissional_service import buscar_profissional


async def _verificar_dono(db: AsyncSession, profissional_id: str, usuario: Usuario) -> None:
    profissional = await buscar_profissional(db, profissional_id)
    if profissional.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Acesso negado")


async def criar_servico(
    db: AsyncSession,
    profissional_id: str,
    data: ServicoCreate,
    usuario: Usuario,
) -> Servico:
    await _verificar_dono(db, profissional_id, usuario)

    servico = Servico(
        profissional_id=profissional_id,
        nome=data.nome,
        descricao=data.descricao,
        preco=data.preco,
        duracao_minutos=data.duracao_minutos,
    )
    db.add(servico)
    await db.commit()
    await db.refresh(servico)
    return servico


async def listar_servicos_do_profissional(
    db: AsyncSession, profissional_id: str
) -> list[Servico]:
    await buscar_profissional(db, profissional_id)
    result = await db.execute(
        select(Servico).where(
            Servico.profissional_id == profissional_id,
            Servico.deleted_at.is_(None),
            Servico.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def buscar_servico(db: AsyncSession, servico_id: str) -> Servico:
    result = await db.execute(
        select(Servico).where(
            Servico.id == servico_id,
            Servico.deleted_at.is_(None),
        )
    )
    servico = result.scalar_one_or_none()
    if servico is None:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return servico


async def atualizar_servico(
    db: AsyncSession,
    servico_id: str,
    data: ServicoUpdate,
    usuario: Usuario,
) -> Servico:
    servico = await buscar_servico(db, servico_id)
    await _verificar_dono(db, servico.profissional_id, usuario)

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(servico, campo, valor)

    await db.commit()
    await db.refresh(servico)
    return servico


async def deletar_servico(
    db: AsyncSession, servico_id: str, usuario: Usuario
) -> None:
    servico = await buscar_servico(db, servico_id)
    await _verificar_dono(db, servico.profissional_id, usuario)

    servico.deleted_at = datetime.now(timezone.utc)
    await db.commit()
