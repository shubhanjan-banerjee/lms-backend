import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.logs')
LOG_FILE = os.path.join(LOG_DIR, 'lms_backend.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('lms-backend')
