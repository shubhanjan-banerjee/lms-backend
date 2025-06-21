from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.api.auth import get_current_admin_user
from app.core.database import get_db

router = APIRouter(prefix="/admin/proficiency-levels", tags=["admin-proficiency-levels"])

@router.get("/", response_model=List[schemas.ProficiencyLevelResponse])
async def get_proficiency_levels(
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)],
    skip: int = 0, limit: int = 100
):
    return crud.get_proficiency_levels(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.ProficiencyLevelResponse)
async def create_proficiency_level(
    proficiency: schemas.ProficiencyLevelCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    return crud.create_proficiency_level(db, proficiency)

@router.get("/{proficiency_level_id}", response_model=schemas.ProficiencyLevelResponse)
async def get_proficiency_level_by_id(
    proficiency_level_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_proficiency = crud.get_proficiency_level(db, proficiency_level_id=proficiency_level_id)
    if not db_proficiency:
        raise HTTPException(status_code=404, detail="Proficiency level not found")
    return db_proficiency

@router.delete("/{proficiency_level_id}", response_model=schemas.ProficiencyLevelResponse)
async def delete_proficiency_level(
    proficiency_level_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_proficiency = db.query(models.ProficiencyLevel).filter(models.ProficiencyLevel.id == proficiency_level_id).first()
    if not db_proficiency:
        raise HTTPException(status_code=404, detail="Proficiency level not found")
    db.delete(db_proficiency)
    db.commit()
    return db_proficiency
