from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import joblib
import dramatiq
from dramatiq.brokers.redis import RedisBroker

from src.auth.auth import get_current_user
from src.core.database import get_db
from src.model.models import User, Predictor, Prediction
from src.core.config import configs
from src.core.database import SessionLocal


# Настройка брокера
dramatiq.set_broker(RedisBroker())

router = APIRouter()

with open(configs.SCALER_PATH, 'rb') as file:
    std_scaler = joblib.load(file)


class PredictionInput(BaseModel):
    RIAGENDR: float
    PAQ605: float
    BMXBMI: float
    LBXGLU: float
    DIQ010: float
    LBXGLT: float
    LBXIN: float
    predictor_id: int


class PredictionOut(BaseModel):
    id: int
    status: str
    result: Optional[float] = None
    predictor_name: str
    RIAGENDR: float
    PAQ605: float
    BMXBMI: float
    LBXGLU: float
    DIQ010: float
    LBXGLT: float
    LBXIN: float

    class Config:
        orm_mode = True


@dramatiq.actor
def perform_prediction(predictor_path, need_scale, data_values, prediction_id):
    with SessionLocal() as db:
        new_prediction = db.query(Prediction).get(prediction_id)
        # Загрузить модель
        with open(predictor_path, 'rb') as file:
            model = joblib.load(file)
        # Нормировка входных данных, если необходимо
        if need_scale:
            data_values = std_scaler.transform(data_values)
        # Предсказание модели
        result = int(model.predict(data_values))
        # Запись результата в базу данных
        new_prediction.result = result
        new_prediction.status = "Completed"
        db.commit()


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

    new_prediction = Prediction(
        status="Running",
        RIAGENDR=input_data.RIAGENDR,
        PAQ605=input_data.PAQ605,
        BMXBMI=input_data.BMXBMI,
        LBXGLU=input_data.LBXGLU,
        DIQ010=input_data.DIQ010,
        LBXGLT=input_data.LBXGLT,
        LBXIN=input_data.LBXIN,
        user_id=current_user.id,
        predictor_id=predictor.id
    )
    db.add(new_prediction)
    db.commit()

    try:
        data_values = [[value for key, value in input_data.model_dump().items() if key != "predictor_id"]]
        perform_prediction.send(predictor.path, predictor.need_scale, data_values, new_prediction.id)
        return {"prediction_id": new_prediction.id}

    except Exception as e:
        current_user.balance += predictor.cost
        new_prediction.status = "Failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")


@router.get("/predictions/{prediction_id}", response_model=PredictionOut)
async def get_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prediction = (db.query(Prediction, Predictor.name.label("predictor_name"))
                  .join(Predictor, Prediction.predictor_id == Predictor.id)
                  .filter(Prediction.id == prediction_id)
                  .first())

    if not prediction or prediction.Prediction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Prediction not found or does not belong to the current user")

    prediction_data = prediction.Prediction
    return {
        "id": prediction_data.id,
        "status": prediction_data.status,
        "result": prediction_data.result,
        "predictor_name": prediction.predictor_name,
        "RIAGENDR": prediction_data.RIAGENDR,
        "PAQ605": prediction_data.PAQ605,
        "BMXBMI": prediction_data.BMXBMI,
        "LBXGLU": prediction_data.LBXGLU,
        "DIQ010": prediction_data.DIQ010,
        "LBXGLT": prediction_data.LBXGLT,
        "LBXIN": prediction_data.LBXIN
    }


@router.get("/predictions", response_model=List[PredictionOut])
async def get_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    predictions = (db.query(
                      Prediction.id,
                      Prediction.status,
                      Prediction.result,
                      Predictor.name.label("predictor_name"),
                      Prediction.RIAGENDR,
                      Prediction.PAQ605,
                      Prediction.BMXBMI,
                      Prediction.LBXGLU,
                      Prediction.DIQ010,
                      Prediction.LBXGLT,
                      Prediction.LBXIN
                   )
                   .join(Predictor, Prediction.predictor_id == Predictor.id)
                   .filter(Prediction.user_id == current_user.id)
                   .all())

    return [
        PredictionOut(
            id=pred.id,
            status=pred.status,
            result=pred.result,
            predictor_name=pred.predictor_name,
            RIAGENDR=pred.RIAGENDR,
            PAQ605=pred.PAQ605,
            BMXBMI=pred.BMXBMI,
            LBXGLU=pred.LBXGLU,
            DIQ010=pred.DIQ010,
            LBXGLT=pred.LBXGLT,
            LBXIN=pred.LBXIN
        )
        for pred in predictions
    ]
