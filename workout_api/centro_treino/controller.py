from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException
from pydantic import UUID4
from sqlalchemy import select
from workout_api.centro_treino.models import CentroTreinoModel
from workout_api.centro_treino.schemas import CentroIn, CentroOut
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    "/",
    summary="Criar um novo centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroOut,
)
async def post(
    db_session: DatabaseDependency, centro_in: CentroIn = Body(...)
) -> CentroOut:
    try:
        centro_out = CentroOut(id=uuid4(), **centro_in.model_dump())
        centro_model = CentroTreinoModel(**centro_out.model_dump())

        db_session.add(centro_model)
        await db_session.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um centro de treinamento com o nome: {centro_out.nome}",
        )
    return centro_out


@router.get(
    "/",
    summary="Consultar todos os centros de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=list[CentroOut],
)
async def query(db_session: DatabaseDependency) -> CentroOut:
    centros: list[CentroOut] = (
        (await db_session.execute(select(CentroTreinoModel))).scalars().all()
    )

    return centros


@router.get(
    "/{id}",
    summary="Consultar um centro de treinamento pelo id",
    status_code=status.HTTP_200_OK,
    response_model=CentroOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> CentroOut:
    centro: CentroOut = (
        (await db_session.execute(select(CentroTreinoModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not centro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"centro com id {id} não encontrado",
        )

    return centro


@router.get(
    "/centro_treinamento/{nome}",
    summary="Consultar dados de centro de treinamento pelo nome",
    status_code=status.HTTP_200_OK,
    response_model=List[CentroOut],
)
async def query(db_session: DatabaseDependency, nome: str) -> List[CentroOut]:
    query = select(CentroTreinoModel)
    CentroTreinoModel.nome
    if nome:
        query = query.where(CentroTreinoModel.nome.ilike(f"%{nome}%"))

    centros = (await db_session.execute(query)).scalars().all()

    if not centros:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro de treinamento com nome {nome} não encontrado",
        )

    return centros
