import uvicorn
from src.presentation.app import get_app
from src.container import APP_CONTAINER
from src.parsers.json_curr import JsonCurrParser
from src.settings import logging_config

if __name__ == "__main__":
    db = APP_CONTAINER.database()
    db.insert_currencies(currencies=JsonCurrParser().parse_county_curr())

    app = get_app()
    settings = APP_CONTAINER.app_settings()
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
