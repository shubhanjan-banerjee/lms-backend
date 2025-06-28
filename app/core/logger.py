import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.core.config import LOG_LEVEL

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.logs')
# Add timestamp to log file name for each server start
log_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f'lms_backend_{log_timestamp}.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure root logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('lms-backend')

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    """
    return logging.getLogger(f'lms-backend.{name}')
