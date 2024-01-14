from sqlmodel import SQLModel, Column, Integer, String, Field, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
#from src.model.prediction import Prediction
from typing import List
#from src.model.base_model import BaseModel


class User(SQLModel, table=True):
    # id: int = Column(Integer, primary_key=True)
    # name: str = Column(String, unique=True, nullable=False)
    # password: str = Column(String, nullable=False)
    # balance: int = Column(Integer, nullable=False, default=500)
    # user_token: str = Column(String, unique=True, nullable=False)
    # prediction = relationship('Prediction', back_populates='user')
    # id: int = Field(primary_key=True)
    # name: str = Text()
    # password: str = Text()
    # token: str = Field(unique=True)
    # balance: int = Field(default=500)
    #name: str = Field(default=None, nullable=True)
    #is_active: bool = Field(default=True)
    #is_superuser: bool = Field(default=False)
    #predictions: list = Field(default=None, nullable=True)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    balance: Mapped[int] = mapped_column(nullable=False, default=500)
    user_token: Mapped[str] = mapped_column(unique=True, nullable=False)
    predictions = Mapped[List["Prediction"]] = relationship(back_populates="user")

class Prediction(SQLModel, table=True):
    # id: int = Field(primary_key=True)
    # created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=func.now()))
    # predicted_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    # predictor: str = Field(sa_column=Column(String), foreign_keys=[Predictor.name])
    # input_data: str = Field(sa_column=Column(String))
    # output_data: str = Field(sa_column=Column(String))

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
    predictor_id: Mapped[str] = mapped_column(ForeignKey("predictor.id"))
    user = Mapped["User"] = relationship(back_populates="prediction")

class Predictor(SQLModel, table=True):
    name: str = Field(unique=True)
    cost: int = Field()
    # is_active: bool = Field(default=True)