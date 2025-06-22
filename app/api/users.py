from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.api.auth import get_current_admin_user
from app.core.database import get_db
import logging

logger = logging.getLogger("lms_backend.api.users")

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

@router.get("/", response_model=List[schemas.UserResponse])
async def read_all_users(
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)],
    skip: int = 0, limit: int = 100
):
    logger.debug("Fetching all users.")
    try:
        users = crud.get_users(db, skip=skip, limit=limit)
        logger.info(f"Fetched {len(users)} users.")
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise

@router.post("/", response_model=schemas.UserResponse)
async def create_new_user(
    user: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    logger.debug(f"Creating new user with SSO ID: {user.sso_id}")
    db_user = crud.get_user_by_sso_id(db, sso_id=user.sso_id)
    if db_user:
        logger.warning(f"Attempt to create user with existing SSO ID: {user.sso_id}")
        raise HTTPException(status_code=400, detail="SSO ID already registered")
    try:
        created_user = crud.create_user(db=db, user=user)
        logger.info(f"User created: {created_user.email}")
        return created_user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    logger.debug(f"Fetching user by ID: {user_id}")
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User found: {db_user.email}")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_existing_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    logger.debug(f"Updating user ID {user_id}")
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        logger.warning(f"User not found for update: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    try:
        updated_user = crud.update_user(db=db, user_id=user_id, user=user_update)
        logger.info(f"User updated: {updated_user.email}")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise

@router.delete("/{user_id}", response_model=schemas.UserResponse)
async def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    logger.debug(f"Deleting user ID {user_id}")
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        logger.warning(f"User not found for deletion: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User deleted: {db_user.email}")
    return db_user

@router.post("/{user_id}/skills", response_model=schemas.UserSkillResponse)
async def add_user_skill(
    user_id: int,
    user_skill: schemas.UserSkillCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    logger.debug(f"Adding skill to user ID {user_id}: {user_skill.skill_id}")
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        logger.warning(f"User not found for skill addition: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    db_skill = crud.get_skill(db, skill_id=user_skill.skill_id)
    if not db_skill:
        logger.warning(f"Skill not found: {user_skill.skill_id}")
        raise HTTPException(status_code=404, detail="Skill not found")
    db_proficiency = crud.get_proficiency_level(db, proficiency_level_id=user_skill.proficiency_level_id)
    if not db_proficiency:
        logger.warning(f"Proficiency level not found: {user_skill.proficiency_level_id}")
        raise HTTPException(status_code=404, detail="Proficiency level not found")
    existing_user_skill = db.query(models.UserSkill).filter(
        models.UserSkill.user_id == user_id,
        models.UserSkill.skill_id == user_skill.skill_id
    ).first()
    if existing_user_skill:
        logger.info(f"Updating existing skill for user ID {user_id}: {user_skill.skill_id}")
        existing_user_skill.proficiency_level_id = user_skill.proficiency_level_id
        db.add(existing_user_skill)
        db.commit()
        db.refresh(existing_user_skill)
        return existing_user_skill
    else:
        logger.info(f"Adding new skill for user ID {user_id}: {user_skill.skill_id}")
        new_user_skill = models.UserSkill(**user_skill.dict())
        db.add(new_user_skill)
        db.commit()
        db.refresh(new_user_skill)
        return new_user_skill
