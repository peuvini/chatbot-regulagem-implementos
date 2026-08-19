from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_admin
from app.modules.auth.models import User
from app.modules.ml.schemas import ModelInfo, PredictionInput, PredictionOutput
from app.modules.ml.service import MLService


router = APIRouter(prefix="/ml", tags=["machine-learning"])


@router.get("/model", response_model=ModelInfo)
def model_info(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return MLService(db).load_or_train()


@router.post("/train", response_model=ModelInfo)
def train_model(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return MLService(db).train()


@router.post("/predict", response_model=PredictionOutput)
def predict_power(payload: PredictionInput, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    prediction = MLService(db).predict_power(payload.model_dump())
    return {"predicted_power_hp": round(prediction, 1)}
