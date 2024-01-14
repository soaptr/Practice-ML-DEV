from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.auth.auth import get_current_user
from src.core.database import get_db
from src.model.models import User, Predictor, Prediction


router = APIRouter()


class PredictionInput(BaseModel):
    RIAGENDR: float
    PAQ605: float
    BMXBMI: float
    LBXGLU: float
    DIQ010: float
    LBXGLT: float
    LBXIN: float
    predictor_id: int


@router.post("/predict")
async def make_prediction(
    input_data: PredictionInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    predictor = db.query(Predictor).filter(Predictor.id == input_data.predictor_id).first()
    if not predictor:
        raise HTTPException(status_code=404, detail="Predictor not found")

    # Проверить баланс пользователя и списать деньги
    if current_user.balance < predictor.cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    current_user.balance -= predictor.cost
    db.commit()

    try:
        # Загрузите и используйте модель для предсказания (псевдокод)
        # model = load_model(predictor.path)
        # result = model.predict([input_data...])

        result = 0.0  # Замените это фактическим результатом предсказания

        # Сохранить результат в базе данных
        new_prediction = Prediction(
            status="Completed",
            RIAGENDR=input_data.RIAGENDR,
            PAQ605=input_data.PAQ605,
            BMXBMI=input_data.BMXBMI,
            LBXGLU=input_data.LBXGLU,
            DIQ010=input_data.DIQ010,
            LBXGLT=input_data.LBXGLT,
            LBXIN=input_data.LBXIN,
            result=result,
            user_id=current_user.id,
            predictor_id=predictor.id
        )
        db.add(new_prediction)
        db.commit()

        return {"prediction_id": new_prediction.id, "result": result}

    except Exception as e:
        current_user.balance += predictor.cost
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")
