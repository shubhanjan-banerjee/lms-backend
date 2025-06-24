from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import DATABASE_URL
from app.core.logger import logger
import logging

logger.debug("Create all database tables with error handling")

def create_all_tables(engine, Base):
    try:
        logger.debug("Creating or verifying tables...")
        Base.metadata.create_all(bind=engine)
        logger.debug("Database tables created or verified successfully.")
    except Exception as e:
        logger.error(f"Database connection or table creation failed: {e}")
        print("[ERROR] Could not connect to the database or create tables. Please check your database settings and ensure the server is running.")

engine = create_engine(
    DATABASE_URL, 
    echo=True,
    connect_args={"auth_plugin": "mysql_native_password"}
)

# Add SQL logging handler for more verbose output
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
