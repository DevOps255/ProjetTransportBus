import json
import logging
import os
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):

    """Formateur de logs qui produit du JSON sur structuré sur
    une seule ligne par entrée de log"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry={
            "timestamp":datetime.now(tz=timezone.utc).isoformat(),
            "level":record.levelname,
            "logger":record.name,
            "message":record.getMessage()
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record,"user_id"):
            log_entry["user_id"] = record.user_id

        if hasattr(record,"request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry, ensure_ascii=False)



def configure_logging() -> None:
    environment = os.environ.get("ENVIRONMENT", "development")
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)

    if environment == "production":
        handler.setFormatter(JSONFormatter())
        root_logger.setLevel(logging.INFO)

    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)