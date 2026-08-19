from __future__ import annotations

from pydantic import BaseModel


class ModelMetrics(BaseModel):
    mae_hp: float
    rmse_hp: float
    training_rows: int


class ModelInfo(BaseModel):
    kind: str
    target: str
    features: list[str]
    metrics: ModelMetrics

class PredictionInput(BaseModel):
    largura_mm: float | None = None
    profundidade_media_mm: float | None = None
    espacamento_mm: float | None = None
    peso_medio_kg: float | None = None
    n_discos: float | None = None
    n_hastes: float | None = None
    grupo: str | None = None
    familia: str | None = None


class PredictionOutput(BaseModel):
    predicted_power_hp: float

