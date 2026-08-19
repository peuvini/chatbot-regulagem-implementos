from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.tractors.repository import TractorRepository
from app.modules.tractors.schemas import TractorRead, TractorStats


class TractorService:
    def __init__(self, db: Session):
        self.repository = TractorRepository(db)

    def list_tractors(self, q: str | None = None, limit: int = 80) -> list[TractorRead]:
        return [TractorRead.model_validate(item) for item in self.repository.list(q=q, limit=limit)]

    def stats(self) -> TractorStats:
        return TractorStats(**self.repository.stats())

