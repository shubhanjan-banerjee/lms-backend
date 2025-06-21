from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.api.auth import get_current_admin_user
from app.core.database import get_db

router = APIRouter(prefix="/admin/skills", tags=["admin-skills"])

@router.get("/", response_model=List[schemas.SkillResponse])
async def get_skills(
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)],
    skip: int = 0, limit: int = 100
):
    return crud.get_skills(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.SkillResponse)
async def create_skill(
    skill: schemas.SkillCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    return crud.create_skill(db, skill)

@router.get("/{skill_id}", response_model=schemas.SkillResponse)
async def get_skill_by_id(
    skill_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_skill = crud.get_skill(db, skill_id=skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return db_skill

@router.delete("/{skill_id}", response_model=schemas.SkillResponse)
async def delete_skill(
    skill_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(db_skill)
    db.commit()
    return db_skill
