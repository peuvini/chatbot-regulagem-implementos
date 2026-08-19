from __future__ import annotations

from sqlalchemy import Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from app.core.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_json: Mapped[dict] = mapped_column(JSON)
    response_json: Mapped[dict] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

