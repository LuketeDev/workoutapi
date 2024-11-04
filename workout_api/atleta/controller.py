from datetime import datetime, timezone
import logging
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi_pagination import LimitOffsetPage, Page, add_pagination, paginate
from fastapi_pagination.ext.sqlalchemy import paginate as sqlpag
from pydantic import UUID4
from sqlalchemy import String, select

from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treino.models import CentroTreinoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


# POST Criar atleta
@router.post(
    "/",
    summary="Criar um novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def post(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)):
    categoria_nome = atleta_in.categoria.nome
    categoria = (
        (
            await db_session.execute(
                select(CategoriaModel).filter_by(nome=categoria_nome)
            )
        )
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria {categoria_nome} não foi encontrada",
        )

    centro_nome = atleta_in.centro_treinamento.nome
    centro = (
        (
            await db_session.execute(
                select(CentroTreinoModel).filter_by(nome=centro_nome)
            )
        )
        .scalars()
        .first()
    )

    if not centro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O centro de treinamento {centro_nome} não foi encontrado",
        )
    try:
        atleta_out = AtletaOut(
            id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump()
        )
        atleta_model = AtletaModel(
            **atleta_out.model_dump(exclude={"categoria", "centro_treinamento"})
        )
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treino_id = centro.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except Exception:
        print(Exception)
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um atleta cadastrado com o CPF: {atleta_out.cpf}",
        )
    return atleta_out


# GET Todos atletas
@router.get(
    "/",
    summary="Retorna todos os atletas",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[AtletaOut],
)
async def query(db_session: DatabaseDependency) -> LimitOffsetPage[AtletaOut]:
    query = select(AtletaModel)
    atletas = await sqlpag(db_session, query)
    return atletas


# GET Atleta por UUID
@router.get(
    "/{id}",
    summary="Consultar dados de um atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta com id {id} não encontrado",
        )

    return atleta


# UPDATE por id
@router.patch(
    "/{id}",
    summary="Editar um atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query(
    id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta com id {id} não encontrado",
        )

    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta


# DELETE por id
@router.delete(
    "/{id}", summary="Deletar um atleta pelo id", status_code=status.HTTP_204_NO_CONTENT
)
async def query(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta com id {id} não encontrado",
        )

    await db_session.delete(atleta)
    await db_session.commit()


# GET Atleta por nome
@router.get(
    "/atletas/nome/{nome}",
    summary="Consultar dados de atletas pelo nome",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[AtletaOut],
)
async def query(
    db_session: DatabaseDependency, nome: str
) -> LimitOffsetPage[AtletaOut]:
    query = select(AtletaModel)

    if nome:
        query = query.where(AtletaModel.nome.ilike(f"%{nome}%"))

    atletas = await sqlpag(db_session, query)

    if not atletas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta com nome {nome} não encontrado",
        )

    return atletas


# GET atleta por CPF
@router.get(
    "/atletas/cpf/{cpf}",
    summary="Consultar dados de atletas pelo cpf",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[AtletaOut],
)
async def query(db_session: DatabaseDependency, cpf: str) -> LimitOffsetPage[AtletaOut]:
    query = select(AtletaModel)

    if cpf:
        query = query.where(AtletaModel.cpf.ilike(f"%{cpf}%"))

    atletas = await sqlpag(db_session, query)

    if not atletas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta com cpf {cpf} não encontrado",
        )

    return atletas


@router.get(
    "/atletas/centro_treinamento/{centro_treinamento}",
    summary="Consultar dados de atletas por centro de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[AtletaOut],
)
async def query(
    db_session: DatabaseDependency, centro_treinamento: str
) -> LimitOffsetPage[AtletaOut]:
    query = select(AtletaModel, CentroTreinoModel.nome).join(
        CentroTreinoModel, AtletaModel.centro_treino_id == CentroTreinoModel.pk_id
    )
    if centro_treinamento:
        query = query.where(CentroTreinoModel.nome.ilike(f"%{centro_treinamento}%"))

    logging.info(f"SQL GERADO: {query}")
    atletas = await sqlpag(db_session, query)

    if not atletas.items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"O centro de treinamento {centro_treinamento} não foi encontrado",
        )

    return atletas


add_pagination(router)
