from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_admin
from app.modules.auth.models import User
from app.modules.implements.schemas import ImplementListResponse, ImplementStats
from app.modules.implements.service import ImplementService


router = APIRouter(prefix="/implements", tags=["implements"])


@router.get("", response_model=ImplementListResponse)
def list_implements(
    grupo: str | None = None,
    q: str | None = None,
    familia: str | None = None,
    limit: int = Query(default=80, ge=1, le=500),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    service = ImplementService(db)
    return {"items": service.list_implements(grupo=grupo, q=q, familia=familia, limit=limit)}


@router.get("/stats", response_model=list[ImplementStats])
def implement_stats(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return ImplementService(db).stats_by_group()
