from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.implements.models import Implement
from app.modules.tractors.models import Tractor


class OperationPlanningRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_implements(self, grupo: str) -> list[Implement]:
        stmt = (
            select(Implement)
            .where(Implement.grupo == grupo)
            .where(Implement.largura_mm.is_not(None))
            .order_by(Implement.largura_mm, Implement.potencia_media_hp)
        )
        return list(self.db.scalars(stmt).all())

    def list_tractors(self) -> list[Tractor]:
        stmt = select(Tractor).where(Tractor.potencia_hp.is_not(None)).order_by(Tractor.potencia_hp)
        return list(self.db.scalars(stmt).all())
