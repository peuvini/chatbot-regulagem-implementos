from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.recommendations.models import Recommendation


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, request_json: dict, response_json: dict) -> Recommendation:
        item = Recommendation(request_json=request_json, response_json=response_json)
        self.db.add(item)
        self.db.flush()
        return item

    def list(self, limit: int = 50) -> list[Recommendation]:
        stmt = select(Recommendation).order_by(Recommendation.id.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def delete_all(self) -> None:
        self.db.query(Recommendation).delete()
        self.db.flush()

