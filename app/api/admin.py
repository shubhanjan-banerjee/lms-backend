from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])
# All CRUD endpoints have been moved to their respective modules (users, skills, etc.)
# Add admin-specific endpoints here if needed in the future.
