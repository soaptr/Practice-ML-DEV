import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

ENV: str = ""


class Configs(BaseSettings):
    # base
    ENV: str = os.getenv("ENV", "dev")
    API: str = "/api"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "fca-api"
    ENV_DATABASE_MAPPER: dict = {
        "prod": "fca",
        "dev": "dev-fca",
    }
    DB_ENGINE_MAPPER: dict = {
        "postgresql": "postgresql",
        "sqlite": "sqlite3",
    }

    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # date
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    # auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 60 minutes * 24 hours * 30 days = 30 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # database
    DB: str = os.getenv("DB", "sqlite")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_FILE: str = os.getenv("DB_FILE", "temp.db")
    DB_ENGINE: str = DB_ENGINE_MAPPER.get(DB, "sqlite")

    if DB_ENGINE == "postgresql":
        DATABASE_URI_FORMAT: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}"
        DATABASE_URI: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}".format(
           db_engine=DB_ENGINE,
           user=DB_USER,
           password=DB_PASSWORD,
           host=DB_HOST,
           port=DB_PORT,
           database=ENV_DATABASE_MAPPER[ENV],
        )

    else:
        DATABASE_URI: str = "sqlite:///{dbfile}".format(dbfile=DB_FILE)

    # find query
    PAGE: int = 1
    PAGE_SIZE: int = 20
    ORDERING: str = "-id"

    LOGREG_PATH: str = "src/pickle-models/log_reg.pkl"
    SVM_PATH: str = "src/pickle-models/svm.pkl"
    RANDFOREST_PATH: str = "src/pickle-models/rand_forest.pkl"
    XGBOOST_PATH: str = "src/pickle-models/xgb_classifier.pkl"
    SCALER_PATH: str = "src/pickle-models/std_scaler.pkl"

    class Config:
        case_sensitive = True


class TestConfigs(Configs):
    ENV: str = "test"


configs = Configs()

