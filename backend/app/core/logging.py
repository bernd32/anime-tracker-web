import logging
import sys
from logging.config import dictConfig

from app.core.config import Settings


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


def setup_logging(settings: Settings) -> None:
    config = LOGGING_CONFIG.copy()
    config["root"] = {**config["root"], "level": settings.log_level.upper()}
    dictConfig(config)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
