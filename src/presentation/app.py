from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from src.presentation.router import router, validation_exception_handler


def get_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    return app
