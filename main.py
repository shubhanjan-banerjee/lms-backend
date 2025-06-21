from fastapi import FastAPI
import app.models.models
from app.api import auth
from app.api import users
from app.api import skills
from app.api import proficiency_levels
from app.api import project_roles
from app.api import role_skill_requirements
from app.core.logger import logger

app = FastAPI(
    title="LMS Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(skills.router)
app.include_router(proficiency_levels.router)
app.include_router(project_roles.router)
app.include_router(role_skill_requirements.router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "LMS Backend API is running!"}

def main():
    import uvicorn
    logger.info("Starting LMS Backend API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
