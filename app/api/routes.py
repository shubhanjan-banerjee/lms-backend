from fastapi import APIRouter
from app.api import auth, users, skills, proficiency_levels, project_roles, role_skill_requirements, userupload
from app.api.courses import router as courses_router
from app.api.learning_paths import router as learning_paths_router

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(skills.router)
router.include_router(proficiency_levels.router)
router.include_router(project_roles.router)
router.include_router(role_skill_requirements.router)
router.include_router(userupload.router)
router.include_router(courses_router)
router.include_router(learning_paths_router)
