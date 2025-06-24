from fastapi import APIRouter
from app.core.logger import logger
from sqlalchemy.exc import OperationalError
from app.core.database import SessionLocal
from sqlalchemy.sql import text

router = APIRouter()

@router.get("/", tags=["Root"])
async def root():
    logger.debug("Root endpoint accessed.")
    return {"message": "LMS Backend API is running!"}

@router.get("/db-health", tags=["Health"])
def db_health_check():
    logger.debug("/db-health endpoint accessed.")
    try:
        db = SessionLocal()
        logger.debug("Database session created for health check.")
        db.execute(text("SELECT 1"))
        db.close()
        logger.debug("Database health check successful.")
        return {"status": "ok", "message": "Database connection successful."}
    except OperationalError as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "message": "Database connection failed."}
    except Exception as e:
        logger.error(f"Unexpected error during DB health check: {e}")
        return {"status": "error", "message": "Unexpected error during DB health check."}

@router.get("/api-health", tags=["Health"])
def api_health_check():
    logger.debug("/api-health endpoint accessed.")
    return {"status": "ok", "message": "API is healthy and running."}
