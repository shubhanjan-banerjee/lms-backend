from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.api.auth import get_current_admin_user
from app.core.database import get_db

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

@router.get("/", response_model=List[schemas.UserResponse])
async def read_all_users(
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)],
    skip: int = 0, limit: int = 100
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.UserResponse)
async def create_new_user(
    user: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_user = crud.get_user_by_sso_id(db, sso_id=user.sso_id)
    if db_user:
        raise HTTPException(status_code=400, detail="SSO ID already registered")
    return crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_existing_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user=user_update)

@router.delete("/{user_id}", response_model=schemas.UserResponse)
async def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/{user_id}/skills", response_model=schemas.UserSkillResponse)
async def add_user_skill(
    user_id: int,
    user_skill: schemas.UserSkillCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_skill = crud.get_skill(db, skill_id=user_skill.skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db_proficiency = crud.get_proficiency_level(db, proficiency_level_id=user_skill.proficiency_level_id)
    if not db_proficiency:
        raise HTTPException(status_code=404, detail="Proficiency level not found")
    existing_user_skill = db.query(models.UserSkill).filter(
        models.UserSkill.user_id == user_id,
        models.UserSkill.skill_id == user_skill.skill_id
    ).first()
    if existing_user_skill:
        existing_user_skill.proficiency_level_id = user_skill.proficiency_level_id
        db.add(existing_user_skill)
        db.commit()
        db.refresh(existing_user_skill)
        return existing_user_skill
    else:
        new_user_skill = models.UserSkill(**user_skill.dict())
        db.add(new_user_skill)
        db.commit()
        db.refresh(new_user_skill)
        return new_user_skill
