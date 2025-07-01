from fastapi import APIRouter
from app.api import ai, auth, courses, health, learning_paths, proficiency_levels, project_roles, role_skill_requirements, skills, users, userupload

router = APIRouter()

# Include all routers
router.include_router(ai.router)
router.include_router(auth.router)
router.include_router(health.router)
router.include_router(courses.router)
router.include_router(learning_paths.router)
router.include_router(users.router)
router.include_router(skills.router)
router.include_router(proficiency_levels.router)
router.include_router(project_roles.router)
router.include_router(role_skill_requirements.router)
router.include_router(userupload.router)

