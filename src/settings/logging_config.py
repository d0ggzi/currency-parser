import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s \t %(levelname)s \t %(message)s \t %(funcName)s"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "standard",
        }
    },
    "loggers": {"": {"handlers": ["stdout"], "level": "DEBUG"}},
}


logging.config.dictConfig(LOGGING)
