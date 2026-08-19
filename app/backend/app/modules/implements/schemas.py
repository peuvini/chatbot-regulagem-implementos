from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ImplementBase(BaseModel):
    grupo: str
    familia: str | None = None
    descricao: str | None = None
    modelo: str | None = None
    n_discos: float | None = None
    n_hastes: float | None = None
    largura_mm: float | None = None
    largura_min_mm: float | None = None
    largura_max_mm: float | None = None
    profundidade_min_mm: float | None = None
    profundidade_max_mm: float | None = None
    profundidade_media_mm: float | None = None
    espacamento_mm: float | None = None
    diametro_dos_discos: str | None = None
    peso_18_kg: float | None = None
    peso_20_kg: float | None = None
    peso_22_kg: float | None = None
    peso_24_kg: float | None = None
    peso_26_kg: float | None = None
    peso_28_kg: float | None = None
    peso_30_kg: float | None = None
    peso_32_kg: float | None = None
    peso_34_kg: float | None = None
    peso_36_kg: float | None = None
    peso_aprox_geral_kg: float | None = None
    peso_medio_kg: float | None = None
    potencia_min_hp: float | None = None
    potencia_max_hp: float | None = None
    potencia_media_hp: float | None = None
    potencia_esteira_min_hp: float | None = None
    potencia_esteira_max_hp: float | None = None
    rodeiro: str | None = None
    fonte_imagem: str | None = None
    observacoes: str | None = None
    search_text: str | None = None


class ImplementCreate(ImplementBase):
    pass


class ImplementRead(ImplementBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ImplementListResponse(BaseModel):
    items: list[ImplementRead]


class ImplementStats(BaseModel):
    grupo: str
    total: int
    potencia_media: float | None
    peso_medio: float | None

