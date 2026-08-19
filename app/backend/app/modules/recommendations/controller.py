from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.auth.models import User
from app.modules.recommendations.schemas import RecommendationRead, RecommendationRequest, RecommendationResponse
from app.modules.recommendations.service import RecommendationService


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
def create_recommendation(payload: RecommendationRequest, _user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RecommendationService(db).recommend(payload)


@router.get("/dashboard")
def dashboard(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return RecommendationService(db).dashboard()


@router.get("", response_model=list[RecommendationRead])
def list_recommendations(
    limit: int = Query(default=50, ge=1, le=200),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return RecommendationService(db).list_recommendations(limit)
