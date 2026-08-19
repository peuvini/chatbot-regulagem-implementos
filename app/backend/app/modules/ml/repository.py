from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.config import get_settings


class MLRepository:
    def __init__(self, model_path: Path | None = None):
        self.model_path = model_path or get_settings().model_path

    def save_model(self, model: dict[str, Any]) -> None:
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_model(self) -> dict[str, Any] | None:
        if not self.model_path.exists():
            return None
        return json.loads(self.model_path.read_text(encoding="utf-8"))

