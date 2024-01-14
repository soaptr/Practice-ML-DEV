from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dependency_injector import providers

from src.core.config import configs
from src.core.database import Database
from src.core.predict import router as predict_router
from src.core.user_predictions import router as user_predictions_router
from src.auth.auth import router as auth_router


class AppCreator:
    def __init__(self):
        # set app default
        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            openapi_url=f"{configs.API}/openapi.json",
            version="0.0.1",
        )

        self.db = providers.Singleton(Database, db_url=configs.DATABASE_URI)()
        self.db.create_database()

        # set cors
        if configs.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # set routes
        @self.app.get("/")
        def root():
            return "service is working"

        self.app.include_router(auth_router, prefix="")
        self.app.include_router(predict_router, prefix="")
        self.app.include_router(user_predictions_router, prefix="")


app_creator = AppCreator()
app = app_creator.app
db = app_creator.db
