from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Implement(Base):
    __tablename__ = "implements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    grupo: Mapped[str] = mapped_column(String(30), index=True)
    familia: Mapped[str | None] = mapped_column(String(120), index=True)
    descricao: Mapped[str | None] = mapped_column(String(255))
    modelo: Mapped[str | None] = mapped_column(String(120), index=True)
    n_discos: Mapped[float | None] = mapped_column(Float)
    n_hastes: Mapped[float | None] = mapped_column(Float)
    largura_mm: Mapped[float | None] = mapped_column(Float)
    largura_min_mm: Mapped[float | None] = mapped_column(Float)
    largura_max_mm: Mapped[float | None] = mapped_column(Float)
    profundidade_min_mm: Mapped[float | None] = mapped_column(Float)
    profundidade_max_mm: Mapped[float | None] = mapped_column(Float)
    profundidade_media_mm: Mapped[float | None] = mapped_column(Float)
    espacamento_mm: Mapped[float | None] = mapped_column(Float)
    diametro_dos_discos: Mapped[str | None] = mapped_column(String(120))
    peso_18_kg: Mapped[float | None] = mapped_column(Float)
    peso_20_kg: Mapped[float | None] = mapped_column(Float)
    peso_22_kg: Mapped[float | None] = mapped_column(Float)
    peso_24_kg: Mapped[float | None] = mapped_column(Float)
    peso_26_kg: Mapped[float | None] = mapped_column(Float)
    peso_28_kg: Mapped[float | None] = mapped_column(Float)
    peso_30_kg: Mapped[float | None] = mapped_column(Float)
    peso_32_kg: Mapped[float | None] = mapped_column(Float)
    peso_34_kg: Mapped[float | None] = mapped_column(Float)
    peso_36_kg: Mapped[float | None] = mapped_column(Float)
    peso_aprox_geral_kg: Mapped[float | None] = mapped_column(Float)
    peso_medio_kg: Mapped[float | None] = mapped_column(Float)
    potencia_min_hp: Mapped[float | None] = mapped_column(Float)
    potencia_max_hp: Mapped[float | None] = mapped_column(Float)
    potencia_media_hp: Mapped[float | None] = mapped_column(Float)
    potencia_esteira_min_hp: Mapped[float | None] = mapped_column(Float)
    potencia_esteira_max_hp: Mapped[float | None] = mapped_column(Float)
    rodeiro: Mapped[str | None] = mapped_column(String(80))
    fonte_imagem: Mapped[str | None] = mapped_column(Text)
    observacoes: Mapped[str | None] = mapped_column(Text)
    search_text: Mapped[str | None] = mapped_column(Text, index=True)

