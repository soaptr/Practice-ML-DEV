from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from src.model.models import User, Predictor
from src.auth.auth import get_current_user
from src.core.database import get_db


router = APIRouter()


class PredictorOut(BaseModel):
    id: int
    name: str
    cost: float


@router.get("/user")
async def get_current_user_data(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "balance": current_user.balance
    }


@router.get("/predictors", response_model=List[PredictorOut])
async def get_all_predictors(db: Session = Depends(get_db)):
    predictors = db.query(Predictor).all()
    return [PredictorOut(id=predictor.id, name=predictor.name, cost=predictor.cost) for predictor in predictors]
