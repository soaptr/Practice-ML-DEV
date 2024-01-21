from contextlib import AbstractContextManager, contextmanager
from typing import Any, Callable

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session

from src.model.models import User, Predictor, Prediction
from src.core.config import configs


# def get_db():
#     with Database(db_url=configs.DATABASE_URI).session() as db:
#         yield db


engine = create_engine(configs.DATABASE_URI, echo=True)
SessionLocal = orm.scoped_session(
    orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db():
    with SessionLocal() as db:
        yield db


@as_declarative()
class BaseModel:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, echo=True)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        User.metadata.create_all(self._engine)
        Predictor.metadata.create_all(self._engine)
        Prediction.metadata.create_all(self._engine)
        # with self.session() as session:
        #     self._initialize_predictors(session)

        # Инициализация начальных данных
        with SessionLocal() as session:
            self._initialize_predictors(session)

    def _initialize_predictors(self, session: Session):
        if session.query(Predictor).count() == 0:
            predictors = [
                Predictor(id=1, name="Логистическая регрессия", cost=30, path=configs.LOGREG_PATH, need_scale=True),
                Predictor(id=2, name="Метод опорных векторов", cost=40, path=configs.SVM_PATH, need_scale=True),
                Predictor(id=3, name="XGBoost", cost=50, path=configs.XGBOOST_PATH, need_scale=False)
            ]
            session.bulk_save_objects(predictors)
            session.commit()

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
