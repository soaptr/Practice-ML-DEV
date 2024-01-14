from sqlmodel import SQLModel, Field, Relationship
from typing import List


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    balance: float = Field(default=500.0, nullable=False)
    predictions: List["Prediction"] = Relationship(back_populates="user")


class Predictor(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(unique=True, nullable=False)
    cost: float = Field(ge=0.0, nullable=False)
    path: str = Field(nullable=False)
    predictions: List["Prediction"] = Relationship(back_populates="predictor")


class Prediction(SQLModel, table=True):
    id: int = Field(primary_key=True)
    status: str = Field(nullable=False)
    RIAGENDR: float = Field(nullable=False)  # Пол участника
    PAQ605: float = Field(nullable=False)  # Информация об уровне физической активности
    BMXBMI: float = Field(nullable=False)  # Индекс массы тела
    LBXGLU: float = Field(nullable=False)  # Уровень глюкозы в крови
    DIQ010: float = Field(nullable=False)  # Диагноз диабета
    LBXGLT: float = Field(nullable=False)  # Тест на толерантность к глюкозе
    LBXIN: float = Field(nullable=False)  # Уровень инсулина
    result: float = Field()
    user_id: int = Field(nullable=False, foreign_key="user.id")
    predictor_id: int = Field(nullable=False, foreign_key="predictor.id")
    user: User = Relationship(back_populates="predictions")
    predictor: Predictor = Relationship(back_populates="predictions")
