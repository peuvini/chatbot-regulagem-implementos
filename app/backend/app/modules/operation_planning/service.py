from __future__ import annotations

from math import ceil

from sqlalchemy.orm import Session

from app.core.utils import normalize_text
from app.modules.implements.schemas import ImplementRead
from app.modules.operation_planning.repository import OperationPlanningRepository
from app.modules.operation_planning.schemas import OperationPlanningRequest, OperationPlanningResponse, OperationSizing, TimeDistribution
from app.modules.tractors.schemas import TractorRead


class OperationPlanningService:
    def __init__(self, db: Session):
        self.repository = OperationPlanningRepository(db)

    def calculate(self, payload: OperationPlanningRequest) -> OperationPlanningResponse:
        days = (payload.end_date - payload.start_date).days
        total_hours = days * payload.hours_per_day
        time_distribution = TimeDistribution(
            days=days,
            hours_per_day=payload.hours_per_day,
            total_available_hours=round(total_hours, 2),
            plow_hours=round(total_hours * (2 / 3), 2),
            harrow_total_hours=round(total_hours * (1 / 3), 2),
            harrow_breaking_hours=round((total_hours * (1 / 3)) / 2, 2),
            harrow_leveling_hours=round((total_hours * (1 / 3)) / 2, 2),
        )

        tractors = self.repository.list_tractors()
        implements = self.repository.list_implements("ARADO") + self.repository.list_implements("GRADE")

        operations = [
            self._build_operation(
                key="plow",
                name="Aracao",
                grupo="ARADO",
                area_ha=payload.area_ha,
                area_factor=1,
                available_hours=time_distribution.plow_hours,
                speed_kmh=5.5,
                field_efficiency=0.85,
                implements=implements,
                tractors=tractors,
                formula="L arado = RO arado x 10 / (5,5 x 0,85)",
            ),
            self._build_operation(
                key="breaking_harrow",
                name="Gradagem destorroadora",
                grupo="GRADE",
                area_ha=payload.area_ha,
                area_factor=2,
                available_hours=time_distribution.harrow_breaking_hours,
                speed_kmh=7.0,
                field_efficiency=0.90,
                implements=implements,
                tractors=tractors,
                subtype="breaking",
                formula="L grade destorroadora = RO grade destorroadora x 10 / (7,0 x 0,90)",
            ),
            self._build_operation(
                key="leveling_harrow",
                name="Gradagem niveladora",
                grupo="GRADE",
                area_ha=payload.area_ha,
                area_factor=2,
                available_hours=time_distribution.harrow_leveling_hours,
                speed_kmh=10.0,
                field_efficiency=0.90,
                implements=implements,
                tractors=tractors,
                subtype="leveling",
                formula="L grade niveladora = RO grade niveladora x 10 / (10 x 0,90)",
            ),
        ]

        final_report = [
            f"{operation.equipment_count} conjunto(s) de trator + {operation.name.lower()}"
            + (f" ({operation.implement.modelo})" if operation.implement else "")
            for operation in operations
        ]

        return OperationPlanningResponse(
            input=payload,
            time_distribution=time_distribution,
            operations=operations,
            final_report=final_report,
            formulas=[
                "TD = (data final - data inicial) x horas por dia",
                "TD arado = TD x 2/3",
                "TD grades = TD x 1/3",
                "TD grade destorroadora = TD grades / 2",
                "TD grade niveladora = TD grades / 2",
                "RO arado = area / TD arado",
                "RO grades = area x 2 / TD da operacao",
                "L = RO x 10 / (velocidade x eficiencia de campo)",
                "N equipamentos = teto(RO x 10 / (largura selecionada x velocidade x eficiencia))",
            ],
        )

    def _build_operation(
        self,
        key: str,
        name: str,
        grupo: str,
        area_ha: float,
        area_factor: float,
        available_hours: float,
        speed_kmh: float,
        field_efficiency: float,
        implements,
        tractors,
        formula: str,
        subtype: str | None = None,
    ) -> OperationSizing:
        area_considered = area_ha * area_factor
        operational_rhythm = area_considered / available_hours
        required_width = (operational_rhythm * 10) / (speed_kmh * field_efficiency)
        selected_implement = self._select_implement(implements, grupo, required_width, subtype)
        selected_width_m = (selected_implement.largura_mm / 1000) if selected_implement and selected_implement.largura_mm else None
        required_power = self._required_power(selected_implement)
        tractor = self._select_tractor(tractors, required_power)
        equipment_count = 0
        notes = []

        if selected_width_m:
            equipment_count = max(1, ceil((operational_rhythm * 10) / (selected_width_m * speed_kmh * field_efficiency)))
        else:
            notes.append("Nao foi encontrada largura de trabalho valida para a operacao.")

        if selected_implement and selected_width_m and selected_width_m < required_width:
            notes.append("Nenhum implemento atingiu a largura minima calculada; foi selecionado o maior disponivel.")
        if selected_implement and required_power and not tractor:
            notes.append("Nao foi encontrado trator com potencia suficiente para o implemento selecionado.")

        return OperationSizing(
            key=key,
            name=name,
            area_factor=area_factor,
            area_considered_ha=round(area_considered, 2),
            available_hours=round(available_hours, 2),
            speed_kmh=speed_kmh,
            field_efficiency=field_efficiency,
            operational_rhythm_ha_h=round(operational_rhythm, 3),
            required_width_m=round(required_width, 3),
            selected_width_m=round(selected_width_m, 3) if selected_width_m else None,
            required_power_hp=round(required_power, 1) if required_power else None,
            equipment_count=equipment_count,
            implement=ImplementRead.model_validate(selected_implement) if selected_implement else None,
            tractor=TractorRead.model_validate(tractor) if tractor else None,
            formula=formula,
            notes=notes,
        )

    def _select_implement(self, implements, grupo: str, required_width_m: float, subtype: str | None):
        rows = [row for row in implements if row.grupo == grupo and row.largura_mm]
        if subtype == "leveling":
            rows = [row for row in rows if "nivel" in normalize_text(f"{row.descricao} {row.familia} {row.modelo}")]
        elif subtype == "breaking":
            preferred = [
                row
                for row in rows
                if "nivel" not in normalize_text(f"{row.descricao} {row.familia} {row.modelo}")
                and any(term in normalize_text(f"{row.descricao} {row.familia} {row.modelo}") for term in ("aradora", "intermediaria", "controle"))
            ]
            rows = preferred or [row for row in rows if "nivel" not in normalize_text(f"{row.descricao} {row.familia} {row.modelo}")]

        if not rows:
            return None

        required_width_mm = required_width_m * 1000
        compatible = [row for row in rows if row.largura_mm and row.largura_mm >= required_width_mm]
        if compatible:
            return sorted(compatible, key=lambda row: (row.largura_mm or 0, row.potencia_media_hp or 0))[0]
        return sorted(rows, key=lambda row: row.largura_mm or 0, reverse=True)[0]

    @staticmethod
    def _required_power(implement) -> float | None:
        if not implement:
            return None
        return implement.potencia_max_hp or implement.potencia_media_hp or implement.potencia_min_hp

    @staticmethod
    def _select_tractor(tractors, required_power: float | None):
        if required_power is None:
            return tractors[0] if tractors else None
        compatible = [tractor for tractor in tractors if tractor.potencia_hp and tractor.potencia_hp >= required_power]
        if compatible:
            return sorted(compatible, key=lambda tractor: tractor.potencia_hp or 0)[0]
        return sorted(tractors, key=lambda tractor: tractor.potencia_hp or 0, reverse=True)[0] if tractors else None
