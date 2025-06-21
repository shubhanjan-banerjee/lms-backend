from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.api.auth import get_current_admin_user
from app.core.database import get_db

router = APIRouter(prefix="/admin/role-skill-requirements", tags=["admin-role-skill-requirements"])

@router.get("/", response_model=List[schemas.RoleSkillRequirementResponse])
async def get_role_skill_requirements(
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)],
    skip: int = 0, limit: int = 100
):
    return crud.get_role_skill_requirements(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.RoleSkillRequirementResponse)
async def create_role_skill_requirement(
    req: schemas.RoleSkillRequirementCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    return crud.create_role_skill_requirement(db, req)

@router.get("/{req_id}", response_model=schemas.RoleSkillRequirementResponse)
async def get_role_skill_requirement_by_id(
    req_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_req = crud.get_role_skill_requirement(db, req_id=req_id)
    if not db_req:
        raise HTTPException(status_code=404, detail="Role skill requirement not found")
    return db_req

@router.delete("/{req_id}", response_model=schemas.RoleSkillRequirementResponse)
async def delete_role_skill_requirement(
    req_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_req = db.query(models.RoleSkillRequirement).filter(models.RoleSkillRequirement.id == req_id).first()
    if not db_req:
        raise HTTPException(status_code=404, detail="Role skill requirement not found")
    db.delete(db_req)
    db.commit()
    return db_req
