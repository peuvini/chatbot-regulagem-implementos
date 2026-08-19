from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.operation_planning.schemas import OperationPlanningRequest, OperationPlanningResponse
from app.modules.operation_planning.service import OperationPlanningService


router = APIRouter(prefix="/operation-planning", tags=["operation-planning"])


@router.post("/calculate", response_model=OperationPlanningResponse)
def calculate_operation_plan(
    payload: OperationPlanningRequest,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OperationPlanningService(db).calculate(payload)
