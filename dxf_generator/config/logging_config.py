import logging
import sys
import os
import json
from datetime import datetime
from dxf_generator.config.env_config import config

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if they exist
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
            
        return json.dumps(log_data)

def setup_logging():
    """Configure centralized logging for the application."""
    # Ensure logs directory exists
    log_dir = os.path.join(os.getcwd(), config.LOG_DIR)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Base logger
    logger = logging.getLogger("dxf_generator")
    # Set to DEBUG to capture all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG)

    # Standard Console Handler (Human readable for development)
    console_handler = logging.StreamHandler(sys.stdout)
    # Set console to DEBUG to show everything as requested by user
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # JSON File Handler (Structured for production/monitoring)
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.json.log"))
    # File captures everything including DEBUG and ERROR
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)

    return logger

# Initialize logger instance
logger = setup_logging()
