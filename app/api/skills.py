from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.api.auth import get_current_admin_user
from app.core.database import get_db
import logging

logger = logging.getLogger("lms_backend.api.skills")

router = APIRouter(prefix="/admin/skills", tags=["admin-skills"])

@router.get("/", response_model=List[schemas.SkillResponse])
async def get_skills(
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)],
    skip: int = 0, limit: int = 100
):
    logger.debug(f"Fetching skills with skip={skip}, limit={limit}")
    try:
        skills = crud.get_skills(db, skip=skip, limit=limit)
        logger.info(f"Fetched {len(skills)} skills.")
        return skills
    except Exception as e:
        logger.error(f"Error fetching skills: {e}")
        raise

@router.post("/", response_model=schemas.SkillResponse)
async def create_skill(
    skill: schemas.SkillCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    logger.debug(f"Creating skill: {skill.name}")
    try:
        created_skill = crud.create_skill(db, skill)
        logger.info(f"Skill created: {created_skill.name}")
        return created_skill
    except Exception as e:
        logger.error(f"Error creating skill: {e}")
        raise

@router.get("/{skill_id}", response_model=schemas.SkillResponse)
async def get_skill_by_id(
    skill_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    logger.debug(f"Fetching skill by ID: {skill_id}")
    db_skill = crud.get_skill(db, skill_id=skill_id)
    if not db_skill:
        logger.warning(f"Skill not found: {skill_id}")
        raise HTTPException(status_code=404, detail="Skill not found")
    logger.info(f"Skill found: {db_skill.name}")
    return db_skill

@router.delete("/{skill_id}", response_model=schemas.SkillResponse)
async def delete_skill(
    skill_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    logger.debug(f"Deleting skill ID: {skill_id}")
    db_skill = crud.get_skill(db, skill_id=skill_id)
    if not db_skill:
        logger.warning(f"Skill not found for deletion: {skill_id}")
        raise HTTPException(status_code=404, detail="Skill not found")
    try:
        db.delete(db_skill)
        db.commit()
        logger.info(f"Skill deleted: {db_skill.name}")
        return db_skill
    except Exception as e:
        logger.error(f"Error deleting skill: {e}")
        raise
