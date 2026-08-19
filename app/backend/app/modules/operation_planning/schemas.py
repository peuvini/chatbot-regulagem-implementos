from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from app.modules.implements.schemas import ImplementRead
from app.modules.tractors.schemas import TractorRead


class OperationPlanningRequest(BaseModel):
    area_ha: float = Field(gt=0, examples=[120])
    start_date: date
    end_date: date
    hours_per_day: float = Field(default=8, gt=0, le=24)

    @field_validator("end_date")
    @classmethod
    def validate_period(cls, end_date: date, info: ValidationInfo) -> date:
        start_date = info.data.get("start_date")
        if start_date and end_date <= start_date:
            raise ValueError("A data final deve ser posterior à data inicial.")
        return end_date


class TimeDistribution(BaseModel):
    days: int
    hours_per_day: float
    total_available_hours: float
    plow_hours: float
    harrow_total_hours: float
    harrow_breaking_hours: float
    harrow_leveling_hours: float


class OperationSizing(BaseModel):
    key: str
    name: str
    area_factor: float
    area_considered_ha: float
    available_hours: float
    speed_kmh: float
    field_efficiency: float
    operational_rhythm_ha_h: float
    required_width_m: float
    selected_width_m: float | None
    required_power_hp: float | None
    equipment_count: int
    implement: ImplementRead | None
    tractor: TractorRead | None
    formula: str
    notes: list[str]


class OperationPlanningResponse(BaseModel):
    input: OperationPlanningRequest
    time_distribution: TimeDistribution
    operations: list[OperationSizing]
    final_report: list[str]
    formulas: list[str]
