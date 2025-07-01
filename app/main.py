from fastapi import FastAPI
from app.core.database import engine, Base, create_all_tables
import app.models.models
from app.core.logger import logger
from app.core.db_check import check_database_connectivity
from sqlalchemy.engine.url import make_url
from app.api.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

logger.debug("Starting LMS Backend API initialization...")

# Create all database tables with error handling
# create_all_tables(engine, Base)

# Check database connectivity at startup
check_database_connectivity()

app = FastAPI(
    title="LMS Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration
origins = [
    "*"  # Allow all origins. For production, specify allowed domains, e.g. ["https://your-frontend.com"]
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.debug("Including API routers...")
app.include_router(api_router)
logger.debug("All routers included.")

def start():
    import uvicorn
    logger.debug("Starting LMS Backend API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

logger.debug("LMS Backend API initialization complete. Ready to accept requests.")
