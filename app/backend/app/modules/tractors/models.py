from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tractor(Base):
    __tablename__ = "tractors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str | None] = mapped_column(String(255), index=True)
    potencia_hp: Mapped[float | None] = mapped_column(Float, index=True)
    peso_kg: Mapped[float | None] = mapped_column(Float)
    tracao: Mapped[str | None] = mapped_column(String(80))
    tdp: Mapped[str | None] = mapped_column(String(80))
    tipo_transmissao: Mapped[str | None] = mapped_column(String(120))
    search_text: Mapped[str | None] = mapped_column(Text, index=True)

