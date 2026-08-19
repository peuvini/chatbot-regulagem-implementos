from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.utils import normalize_text
from app.modules.tractors.models import Tractor
from app.modules.tractors.schemas import TractorCreate


class TractorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_many(self, items: list[TractorCreate]) -> int:
        objects = [Tractor(**item.model_dump()) for item in items]
        self.db.add_all(objects)
        self.db.flush()
        return len(objects)

    def delete_all(self) -> None:
        self.db.query(Tractor).delete()
        self.db.flush()

    def list(self, q: str | None = None, limit: int = 80) -> list[Tractor]:
        stmt = select(Tractor)
        if q:
            stmt = stmt.where(Tractor.search_text.like(f"%{normalize_text(q)}%"))
        stmt = stmt.order_by(Tractor.potencia_hp).limit(limit)
        return list(self.db.scalars(stmt).all())

    def stats(self) -> dict:
        stmt = select(
            func.count(Tractor.id).label("total"),
            func.min(Tractor.potencia_hp).label("potencia_min"),
            func.max(Tractor.potencia_hp).label("potencia_max"),
            func.avg(Tractor.potencia_hp).label("potencia_media"),
        )
        row = self.db.execute(stmt).one()
        item = dict(row._mapping)
        for key in ("potencia_min", "potencia_max", "potencia_media"):
            item[key] = round(float(item[key]), 1) if item[key] is not None else None
        return item
