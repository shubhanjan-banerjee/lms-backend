from fastapi import APIRouter
from app.api import auth, users, skills, proficiency_levels, project_roles, role_skill_requirements

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(skills.router)
router.include_router(proficiency_levels.router)
router.include_router(project_roles.router)
router.include_router(role_skill_requirements.router)
