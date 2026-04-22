from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models.usuario import RoleEnum, Usuario
from app.schemas.horario_trabalho import HorarioTrabalhoCreate, HorarioTrabalhoPublic, HorarioTrabalhoUpdate
from app.schemas.servico import ServicoCreate, ServicoPublic, ServicoUpdate
from app.services import horario_service, servico_service

servicos_router = APIRouter(
    prefix="/profissionais/{profissional_id}/servicos",
    tags=["serviços"],
)


@servicos_router.post("/", response_model=ServicoPublic, status_code=status.HTTP_201_CREATED)
async def criar_servico(
    profissional_id: str,
    data: ServicoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_role(RoleEnum.profissional)),
):
    return await servico_service.criar_servico(db, profissional_id, data, usuario)


@servicos_router.get("/", response_model=list[ServicoPublic])
async def listar_servicos(profissional_id: str, db: AsyncSession = Depends(get_db)):
    return await servico_service.listar_servicos_do_profissional(db, profissional_id)


@servicos_router.patch("/{servico_id}", response_model=ServicoPublic)
async def atualizar_servico(
    profissional_id: str,
    servico_id: str,
    data: ServicoUpdate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_role(RoleEnum.profissional)),
):
    return await servico_service.atualizar_servico(db, servico_id, data, usuario)


@servicos_router.delete("/{servico_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_servico(
    profissional_id: str,
    servico_id: str,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_role(RoleEnum.profissional)),
):
    await servico_service.deletar_servico(db, servico_id, usuario)


horarios_router = APIRouter(
    prefix="/profissionais/{profissional_id}/horarios",
    tags=["horários"],
)


@horarios_router.post("/", response_model=HorarioTrabalhoPublic, status_code=status.HTTP_201_CREATED)
async def criar_horario(
    profissional_id: str,
    data: HorarioTrabalhoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_role(RoleEnum.profissional)),
):
    return await horario_service.criar_horario(db, profissional_id, data, usuario)


@horarios_router.get("/", response_model=list[HorarioTrabalhoPublic])
async def listar_horarios(profissional_id: str, db: AsyncSession = Depends(get_db)):
    return await horario_service.listar_horarios_do_profissional(db, profissional_id)


@horarios_router.patch("/{horario_id}", response_model=HorarioTrabalhoPublic)
async def atualizar_horario(
    profissional_id: str,
    horario_id: str,
    data: HorarioTrabalhoUpdate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_role(RoleEnum.profissional)),
):
    return await horario_service.atualizar_horario(db, horario_id, data, usuario)


@horarios_router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_horario(
    profissional_id: str,
    horario_id: str,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_role(RoleEnum.profissional)),
):
    await horario_service.deletar_horario(db, horario_id, usuario)
