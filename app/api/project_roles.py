from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.api.auth import get_current_admin_user
from app.core.database import get_db

router = APIRouter(prefix="/admin/project-roles", tags=["admin-project-roles"])

@router.get("/", response_model=List[schemas.ProjectRoleResponse])
async def get_project_roles(
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)],
    skip: int = 0, limit: int = 100
):
    return crud.get_project_roles(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.ProjectRoleResponse)
async def create_project_role(
    role: schemas.ProjectRoleCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    return crud.create_project_role(db, role)

@router.get("/{role_id}", response_model=schemas.ProjectRoleResponse)
async def get_project_role_by_id(
    role_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_role = crud.get_project_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Project role not found")
    return db_role

@router.delete("/{role_id}", response_model=schemas.ProjectRoleResponse)
async def delete_project_role(
    role_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
):
    db_role = db.query(models.ProjectRole).filter(models.ProjectRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Project role not found")
    db.delete(db_role)
    db.commit()
    return db_role
