from workout_api.contrib.schemas import BaseSchema
from typing import Annotated
from pydantic import UUID4, Field


class CentroIn(BaseSchema):
    nome: Annotated[
        str,
        Field(
            description="Nome do centro de treinamento",
            example="Desafio Fitness",
            max_length=20,
        ),
    ]
    endereco: Annotated[
        str,
        Field(
            description="Endereço do centro de treinamento",
            example="Av. José Moreira dos Santos, qd. 2A, It.3 (Setor Sul)",
            max_lengt=60,
        ),
    ]
    proprietario: Annotated[
        str,
        Field(
            description="Proprietario do centro de treinamento",
            example="Marquin",
            max_lengt=30,
        ),
    ]


class CentroAtleta(BaseSchema):
    nome: Annotated[
        str,
        Field(
            description="Nome do centro de treinamento",
            example="Desafio Fitness",
            max_length=20,
        ),
    ]


class CentroOut(CentroIn):
    id: Annotated[UUID4, Field(description="Identificador do centro de treinamento")]
