from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.utils import normalize_text
from app.modules.implements.models import Implement
from app.modules.implements.schemas import ImplementCreate


class ImplementRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_many(self, items: list[ImplementCreate]) -> int:
        objects = [Implement(**item.model_dump()) for item in items]
        self.db.add_all(objects)
        self.db.flush()
        return len(objects)

    def delete_all(self) -> None:
        self.db.query(Implement).delete()
        self.db.flush()

    def list(self, grupo: str | None = None, q: str | None = None, familia: str | None = None, limit: int = 80) -> list[Implement]:
        stmt = select(Implement)
        q_norm = normalize_text(q)
        if grupo:
            stmt = stmt.where(func.lower(Implement.grupo) == normalize_text(grupo))
        if familia:
            stmt = stmt.where(func.lower(Implement.familia).like(f"%{normalize_text(familia)}%"))
        if q_norm:
            stmt = stmt.where(Implement.search_text.like(f"%{q_norm}%"))
            ordering = case(
                (func.lower(Implement.modelo) == q_norm, 0),
                (func.lower(Implement.modelo).like(f"%{q_norm}%"), 1),
                (func.lower(Implement.familia).like(f"%{q_norm}%"), 2),
                else_=3,
            )
            stmt = stmt.order_by(ordering, Implement.potencia_media_hp)
        else:
            stmt = stmt.order_by(Implement.grupo, Implement.familia, Implement.potencia_media_hp)
        return list(self.db.scalars(stmt.limit(limit)).all())

    def stats_by_group(self) -> list[dict]:
        stmt = (
            select(
                Implement.grupo.label("grupo"),
                func.count(Implement.id).label("total"),
                func.avg(Implement.potencia_media_hp).label("potencia_media"),
                func.avg(Implement.peso_medio_kg).label("peso_medio"),
            )
            .group_by(Implement.grupo)
            .order_by(Implement.grupo)
        )
        output = []
        for row in self.db.execute(stmt).all():
            item = dict(row._mapping)
            item["potencia_media"] = round(float(item["potencia_media"]), 1) if item["potencia_media"] is not None else None
            item["peso_medio"] = round(float(item["peso_medio"]), 1) if item["peso_medio"] is not None else None
            output.append(item)
        return output

    def top_families(self, limit: int = 20) -> list[dict]:
        stmt = (
            select(Implement.familia, Implement.grupo, func.count(Implement.id).label("total"))
            .group_by(Implement.familia, Implement.grupo)
            .order_by(func.count(Implement.id).desc())
            .limit(limit)
        )
        return [dict(row._mapping) for row in self.db.execute(stmt).all()]
