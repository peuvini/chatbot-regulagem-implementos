from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.implements.repository import ImplementRepository
from app.modules.implements.schemas import ImplementRead, ImplementStats


class ImplementService:
    def __init__(self, db: Session):
        self.repository = ImplementRepository(db)

    def list_implements(
        self,
        grupo: str | None = None,
        q: str | None = None,
        familia: str | None = None,
        limit: int = 80,
    ) -> list[ImplementRead]:
        return [ImplementRead.model_validate(item) for item in self.repository.list(grupo, q, familia, limit)]

    def stats_by_group(self) -> list[ImplementStats]:
        return [ImplementStats(**item) for item in self.repository.stats_by_group()]

    def top_families(self, limit: int = 20) -> list[dict]:
        return self.repository.top_families(limit)

