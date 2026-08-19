from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TractorBase(BaseModel):
    nome: str | None = None
    potencia_hp: float | None = None
    peso_kg: float | None = None
    tracao: str | None = None
    tdp: str | None = None
    tipo_transmissao: str | None = None
    search_text: str | None = None


class TractorCreate(TractorBase):
    pass


class TractorRead(TractorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TractorListResponse(BaseModel):
    items: list[TractorRead]


class TractorStats(BaseModel):
    total: int
    potencia_min: float | None
    potencia_max: float | None
    potencia_media: float | None

