from app.core.database import SessionLocal
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from app.core.logger import logger

def check_database_connectivity():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connectivity check at startup: SUCCESS")
    except OperationalError as e:
        logger.error(f"Database connectivity check at startup: FAILED - {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during DB connectivity check at startup: {e}")
        raise
