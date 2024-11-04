from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from workout_api.contrib.models import BaseModel
from workout_api.atleta.models import AtletaModel


class CentroTreinoModel(BaseModel):
    __tablename__ = "centro_treinamento"

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    endereco: Mapped[str] = mapped_column(String(60), nullable=False)
    proprietario: Mapped[str] = mapped_column(String(30), nullable=False)

    atletas: Mapped[list["AtletaModel"]] = relationship(
        "AtletaModel", back_populates="centro_treinamento"
    )
