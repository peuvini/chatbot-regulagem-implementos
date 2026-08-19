from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_admin
from app.modules.auth.models import User
from app.modules.tractors.schemas import TractorListResponse, TractorStats
from app.modules.tractors.service import TractorService


router = APIRouter(prefix="/tractors", tags=["tractors"])


@router.get("", response_model=TractorListResponse)
def list_tractors(
    q: str | None = None,
    limit: int = Query(default=80, ge=1, le=500),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return {"items": TractorService(db).list_tractors(q=q, limit=limit)}


@router.get("/stats", response_model=TractorStats)
def tractor_stats(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return TractorService(db).stats()
