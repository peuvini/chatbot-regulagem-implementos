from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

from app.core.utils import normalize_text
from app.modules.implements.repository import ImplementRepository
from app.modules.implements.schemas import ImplementRead
from app.modules.ml.service import MLService
from app.modules.recommendations.repository import RecommendationRepository
from app.modules.recommendations.schemas import RecommendationRequest, RecommendationResponse
from app.modules.tractors.repository import TractorRepository


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.implement_repository = ImplementRepository(db)
        self.tractor_repository = TractorRepository(db)
        self.recommendation_repository = RecommendationRepository(db)
        self.ml_service = MLService(db)

    def _score(self, row, payload: RecommendationRequest, predicted_power: float) -> tuple[float, list[str]]:
        score = 50.0
        reasons: list[str] = []
        if payload.tractor_power_hp:
            min_hp = row.potencia_min_hp or predicted_power * 0.9
            max_hp = row.potencia_max_hp or predicted_power * 1.1
            if min_hp <= payload.tractor_power_hp <= max_hp:
                score += 35
                reasons.append("potencia do trator dentro da faixa tecnica")
            else:
                distance = min(abs(payload.tractor_power_hp - min_hp), abs(payload.tractor_power_hp - max_hp))
                score -= min(45, distance * 1.4)
                reasons.append("potencia do trator fora da faixa nominal")

        if payload.implement_type and normalize_text(row.grupo) == normalize_text(payload.implement_type):
            score += 12
        if payload.family and normalize_text(payload.family) in normalize_text(row.familia):
            score += 12

        soil = normalize_text(payload.soil_texture)
        moisture = normalize_text(payload.moisture)
        depth = row.profundidade_media_mm or 0
        if "argil" in soil and depth > 180:
            score += 8
            reasons.append("profundidade compativel com preparo mais agressivo em solo argiloso")
        if "aren" in soil and depth > 220:
            score -= 8
            reasons.append("profundidade alta para solo arenoso")
        if "umid" in moisture or "molh" in moisture:
            score -= 6
            reasons.append("umidade elevada aumenta risco de compactacao")

        return max(0, min(100, round(score, 1))), reasons

    def _technical_note(self, row, payload: RecommendationRequest, predicted_power: float) -> str:
        notes = []
        if payload.tractor_power_hp:
            notes.append(f"compatibilidade com trator de {payload.tractor_power_hp} hp")
        soil = normalize_text(payload.soil_texture)
        if "argil" in soil:
            notes.append("solo argiloso pede atencao a umidade e profundidade para evitar compactacao")
        elif "aren" in soil:
            notes.append("solo arenoso tende a exigir menor agressividade")
        if payload.moisture:
            notes.append(f"umidade informada: {payload.moisture}")
        notes.append(f"potencia estimada pelo modelo: {predicted_power:.1f} hp")
        return "; ".join(notes)

    def recommend(self, payload: RecommendationRequest, persist: bool = True) -> RecommendationResponse:
        model = self.ml_service.load_or_train()
        candidates = self.implement_repository.list(
            grupo=payload.implement_type,
            familia=payload.family,
            limit=10000,
        )
        if not candidates:
            candidates = self.implement_repository.list(limit=10000)

        ranked = []
        for row in candidates:
            predicted = self.ml_service.predict_power(row, model)
            score, reasons = self._score(row, payload, predicted)
            ranked.append(
                {
                    "score": score,
                    "reasons": reasons,
                    "ml_predicted_power_hp": round(predicted, 1),
                    "technical_note": self._technical_note(row, payload, predicted),
                    "implement": ImplementRead.model_validate(row),
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        response = RecommendationResponse(
            model_metrics=model["metrics"],
            count=len(ranked),
            recommendations=ranked[: payload.limit],
        )
        if persist:
            self.recommendation_repository.save(payload.model_dump(), response.model_dump())
            self.db.commit()
        return response

    def list_recommendations(self, limit: int = 50):
        return self.recommendation_repository.list(limit)

    def dashboard(self) -> dict:
        model = self.ml_service.load_or_train()
        implements = self.implement_repository.list(limit=10000)
        tractors = self.tractor_repository.list(limit=10000)
        recommendations = self.recommendation_repository.list(limit=500)
        total_implements = len(implements)
        avg_power = self._avg([row.potencia_media_hp for row in implements])
        return {
            "implements": self.implement_repository.stats_by_group(),
            "tractors": self.tractor_repository.stats(),
            "families": self.implement_repository.top_families(),
            "model": model["metrics"],
            "scientific": {
                "data_quality": self._data_quality(implements),
                "power_ranges": self._power_ranges(implements),
                "tractor_power_ranges": self._tractor_power_ranges(tractors),
                "ml_readiness": {
                    "training_coverage_percent": self._percent(model["metrics"]["training_rows"], total_implements),
                    "relative_mae_percent": self._percent(model["metrics"]["mae_hp"], avg_power),
                    "feature_count": len(model.get("features", [])) + len(model.get("groups", [])) + len(model.get("families", [])),
                    "target": model.get("target", "potencia_media_hp"),
                },
                "recommendation_usage": self._recommendation_usage(recommendations),
                "validation_checklist": self._validation_checklist(total_implements, len(tractors), model["metrics"], recommendations),
            },
        }

    def _data_quality(self, implements) -> dict:
        fields = [
            ("modelo", "Modelo"),
            ("largura_mm", "Largura de trabalho"),
            ("peso_medio_kg", "Peso médio"),
            ("potencia_media_hp", "Potência média"),
            ("profundidade_media_mm", "Profundidade"),
        ]
        total = len(implements)
        completeness = []
        for field, label in fields:
            filled = sum(1 for row in implements if getattr(row, field) not in (None, ""))
            completeness.append({"field": field, "label": label, "filled": filled, "missing": total - filled, "percent": self._percent(filled, total)})
        complete_rows = sum(
            1
            for row in implements
            if row.modelo not in (None, "")
            and row.largura_mm is not None
            and row.peso_medio_kg is not None
            and row.potencia_media_hp is not None
        )
        return {
            "total_implements": total,
            "complete_rows": complete_rows,
            "complete_rows_percent": self._percent(complete_rows, total),
            "completeness": completeness,
        }

    def _power_ranges(self, implements) -> list[dict]:
        buckets = [
            ("Até 80 hp", 0, 80),
            ("80 a 120 hp", 80, 120),
            ("120 a 180 hp", 120, 180),
            ("Acima de 180 hp", 180, None),
        ]
        return self._bucketize([row.potencia_media_hp for row in implements], buckets)

    def _tractor_power_ranges(self, tractors) -> list[dict]:
        buckets = [
            ("Até 80 hp", 0, 80),
            ("80 a 120 hp", 80, 120),
            ("120 a 180 hp", 120, 180),
            ("Acima de 180 hp", 180, None),
        ]
        return self._bucketize([row.potencia_hp for row in tractors], buckets)

    def _recommendation_usage(self, recommendations) -> dict:
        scores = []
        requested_soils: Counter[str] = Counter()
        requested_implements: Counter[str] = Counter()
        recommended_groups: Counter[str] = Counter()
        candidate_counts = []

        for item in recommendations:
            request = item.request_json or {}
            response = item.response_json or {}
            if request.get("soil_texture"):
                requested_soils[str(request["soil_texture"])] += 1
            if request.get("implement_type"):
                requested_implements[str(request["implement_type"])] += 1
            recommendations_list = response.get("recommendations") or []
            candidate_counts.append(len(recommendations_list))
            if recommendations_list:
                top = recommendations_list[0]
                if isinstance(top.get("score"), (int, float)):
                    scores.append(float(top["score"]))
                implement = top.get("implement") or {}
                if implement.get("grupo"):
                    recommended_groups[str(implement["grupo"])] += 1

        return {
            "total_recommendations": len(recommendations),
            "avg_top_score": round(self._avg(scores), 1) if scores else 0,
            "avg_returned_items": round(self._avg(candidate_counts), 1) if candidate_counts else 0,
            "top_requested_soils": self._counter_to_list(requested_soils),
            "top_requested_implements": self._counter_to_list(requested_implements),
            "top_recommended_groups": self._counter_to_list(recommended_groups),
        }

    def _validation_checklist(self, total_implements: int, total_tractors: int, metrics: dict, recommendations) -> list[dict]:
        return [
            {
                "label": "Base técnica carregada",
                "status": total_implements >= 50 and total_tractors >= 50,
                "detail": f"{total_implements} implementos e {total_tractors} tratores",
            },
            {
                "label": "Modelo treinado",
                "status": metrics.get("training_rows", 0) >= 50,
                "detail": f"{metrics.get('training_rows', 0)} linhas de treinamento",
            },
            {
                "label": "Erro mensurado",
                "status": metrics.get("mae_hp") is not None and metrics.get("rmse_hp") is not None,
                "detail": f"MAE {metrics.get('mae_hp', 0):.1f} hp · RMSE {metrics.get('rmse_hp', 0):.1f} hp",
            },
            {
                "label": "Uso registrado",
                "status": len(recommendations) > 0,
                "detail": f"{len(recommendations)} recomendações salvas",
            },
        ]

    @staticmethod
    def _bucketize(values, buckets: list[tuple[str, float, float | None]]) -> list[dict]:
        cleaned = [float(value) for value in values if value is not None]
        total = len(cleaned)
        output = []
        for label, minimum, maximum in buckets:
            if maximum is None:
                count = sum(1 for value in cleaned if value >= minimum)
            else:
                count = sum(1 for value in cleaned if minimum <= value < maximum)
            output.append({"label": label, "count": count, "percent": RecommendationService._percent(count, total)})
        return output

    @staticmethod
    def _counter_to_list(counter: Counter[str], limit: int = 6) -> list[dict]:
        total = sum(counter.values())
        return [{"label": label, "count": count, "percent": RecommendationService._percent(count, total)} for label, count in counter.most_common(limit)]

    @staticmethod
    def _avg(values) -> float:
        cleaned = [float(value) for value in values if value is not None]
        if not cleaned:
            return 0.0
        return sum(cleaned) / len(cleaned)

    @staticmethod
    def _percent(part: float, total: float) -> float:
        if not total:
            return 0.0
        return round((float(part) / float(total)) * 100, 1)
