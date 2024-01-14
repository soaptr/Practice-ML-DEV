from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.model.models import User, Prediction
from src.auth.auth import get_current_user
from src.core.database import get_db


router = APIRouter()


@router.get("/predictions", response_model=List[Prediction])
async def get_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).all()
    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions found")
    return predictions
