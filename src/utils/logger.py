import json, logging, sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {"timestamp": datetime.now(timezone.utc).isoformat(), "level": record.levelname, "message": record.getMessage()}
        if record.exc_info: log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def get_logger(name="serverless-ticket-router"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
