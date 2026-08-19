from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
from sqlalchemy.orm import Session

from app.modules.implements.repository import ImplementRepository
from app.modules.ml.repository import MLRepository


FEATURES = [
    "largura_mm",
    "profundidade_media_mm",
    "espacamento_mm",
    "peso_medio_kg",
    "n_discos",
    "n_hastes",
]


class MLService:
    def __init__(self, db: Session, repository: MLRepository | None = None):
        self.db = db
        self.repository = repository or MLRepository()

    @staticmethod
    def _as_float(value: Any) -> float:
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _one_hot(value: str | None, classes: list[str]) -> list[float]:
        return [1.0 if value == item else 0.0 for item in classes]

    def train(self) -> dict[str, Any]:
        rows = ImplementRepository(self.db).list(limit=10000)
        rows = [row for row in rows if row.potencia_media_hp is not None]
        if len(rows) < 10:
            raise RuntimeError("Dados insuficientes para treinar o modelo.")

        groups = sorted({row.grupo for row in rows if row.grupo})
        families = [name for name, _ in Counter(row.familia for row in rows if row.familia).most_common(18)]

        x_raw = []
        y = []
        for row in rows:
            x_raw.append(
                [self._as_float(getattr(row, feature)) for feature in FEATURES]
                + self._one_hot(row.grupo, groups)
                + self._one_hot(row.familia, families)
            )
            y.append(self._as_float(row.potencia_media_hp))

        x = np.array(x_raw, dtype=float)
        target = np.array(y, dtype=float)
        mean = x.mean(axis=0)
        std = x.std(axis=0)
        std[std == 0] = 1.0
        x_scaled = (x - mean) / std
        x_aug = np.concatenate([np.ones((x_scaled.shape[0], 1)), x_scaled], axis=1)

        alpha = 1.0
        regularizer = alpha * np.eye(x_aug.shape[1])
        regularizer[0, 0] = 0.0
        coef = np.linalg.solve(x_aug.T @ x_aug + regularizer, x_aug.T @ target)
        pred = x_aug @ coef

        model = {
            "kind": "ridge_regression_numpy",
            "target": "potencia_media_hp",
            "features": FEATURES,
            "groups": groups,
            "families": families,
            "mean": mean.tolist(),
            "std": std.tolist(),
            "coef": coef.tolist(),
            "metrics": {
                "mae_hp": float(np.mean(np.abs(pred - target))),
                "rmse_hp": float(np.sqrt(np.mean((pred - target) ** 2))),
                "training_rows": len(rows),
            },
        }
        self.repository.save_model(model)
        return model

    def load_or_train(self) -> dict[str, Any]:
        model = self.repository.load_model()
        if model:
            return model
        return self.train()

    def vectorize(self, row: Any, model: dict[str, Any]) -> np.ndarray:
        values = [self._as_float(getattr(row, feature, None) if not isinstance(row, dict) else row.get(feature)) for feature in model["features"]]
        grupo = getattr(row, "grupo", None) if not isinstance(row, dict) else row.get("grupo")
        familia = getattr(row, "familia", None) if not isinstance(row, dict) else row.get("familia")
        values += self._one_hot(grupo, model["groups"])
        values += self._one_hot(familia, model["families"])
        x = np.array(values, dtype=float)
        mean = np.array(model["mean"], dtype=float)
        std = np.array(model["std"], dtype=float)
        return np.concatenate([[1.0], (x - mean) / std])

    def predict_power(self, row: Any, model: dict[str, Any] | None = None) -> float:
        model = model or self.load_or_train()
        coef = np.array(model["coef"], dtype=float)
        return float(self.vectorize(row, model) @ coef)

