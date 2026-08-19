from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.modules.implements.schemas import ImplementRead
from app.modules.ml.schemas import ModelMetrics


class RecommendationRequest(BaseModel):
    implement_type: str | None = Field(default=None, examples=["GRADE"])
    family: str | None = Field(default=None, examples=["NVCR"])
    tractor_power_hp: float | None = Field(default=None, ge=1)
    soil_texture: str | None = Field(default=None, examples=["argiloso"])
    moisture: str | None = Field(default=None, examples=["adequado"])
    crop: str | None = None
    slope: str | None = None
    limit: int = Field(default=8, ge=1, le=20)


class RecommendationItem(BaseModel):
    score: float
    reasons: list[str]
    ml_predicted_power_hp: float
    technical_note: str
    implement: ImplementRead


class RecommendationResponse(BaseModel):
    model_metrics: ModelMetrics
    count: int
    recommendations: list[RecommendationItem]


class RecommendationRead(BaseModel):
    id: int
    request_json: dict
    response_json: dict

    model_config = ConfigDict(from_attributes=True)

