from __future__ import annotations

from sqlalchemy import func, select

from app.core.database import SessionLocal, create_tables
from app.modules.implements.models import Implement
from app.modules.tractors.models import Tractor
from app.scripts.load_data import load_data


def initialize_production() -> dict[str, int | str]:
    """Seed the technical bank once while keeping user-generated data intact."""
    create_tables()
    with SessionLocal() as db:
        implement_count = db.scalar(select(func.count()).select_from(Implement)) or 0
        tractor_count = db.scalar(select(func.count()).select_from(Tractor)) or 0

    if implement_count > 0 and tractor_count > 0:
        return {
            "status": "already_initialized",
            "implements": implement_count,
            "tractors": tractor_count,
        }

    loaded = load_data()
    return {"status": "initialized", **loaded}


if __name__ == "__main__":
    print(initialize_production())
