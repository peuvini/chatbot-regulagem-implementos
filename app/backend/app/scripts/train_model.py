from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.database import SessionLocal, create_tables
from app.modules.ml.service import MLService


def train():
    create_tables()
    with SessionLocal() as db:
        return MLService(db).train()


if __name__ == "__main__":
    model = train()
    print(model["metrics"])

