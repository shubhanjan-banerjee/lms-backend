from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.core.database import get_db
from app.schemas.schemas import PaginatedResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])

@router.post("/", response_model=schemas.LearningPathResponse)
def create_learning_path(lp: schemas.LearningPathCreate, db: Session = Depends(get_db)):
    db_lp = crud.create_learning_path_with_courses(db, lp)
    return db_lp

@router.get("/", response_model=PaginatedResponse[schemas.LearningPathResponse])
def get_learning_paths(
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None, description="Search by learning path name or description"),
    sort_by: str = Query("id", description="Sort by field name"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    total = crud.count_learning_paths(db, search=search)
    lps = crud.get_learning_paths_with_details(db, skip=skip, limit=limit, search=search, sort_by=sort_by, sort_order=sort_order)
    return {"total": total, "items": lps}

@router.get("/{learning_path_id}", response_model=schemas.LearningPathResponse)
def get_learning_path(learning_path_id: int, db: Session = Depends(get_db)):
    lp = crud.get_learning_path_with_details(db, learning_path_id)
    if not lp:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return lp

@router.put("/{learning_path_id}", response_model=schemas.LearningPathResponse)
def update_learning_path(learning_path_id: int, lp: schemas.LearningPathCreate, db: Session = Depends(get_db)):
    db_lp = crud.update_learning_path_with_courses(db, learning_path_id, lp)
    if not db_lp:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return db_lp

@router.delete("/{learning_path_id}", response_model=schemas.LearningPathResponse)
def delete_learning_path(learning_path_id: int, db: Session = Depends(get_db)):
    db_lp = crud.delete_learning_path(db, learning_path_id)
    if not db_lp:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return db_lp

@router.post("/{learning_path_id}/register", response_model=schemas.UserLearningPathResponse)
def register_user_to_learning_path(
    learning_path_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id
    # Check if already registered
    existing = db.query(models.UserLearningPath).filter_by(user_id=user_id, learning_path_id=learning_path_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already registered to this learning path")
    # Check if learning path exists
    lp = db.query(models.LearningPath).filter_by(id=learning_path_id).first()
    if not lp:
        raise HTTPException(status_code=404, detail="Learning path not found")
    # Register
    ulp = models.UserLearningPath(user_id=user_id, learning_path_id=learning_path_id)
    db.add(ulp)
    db.commit()
    db.refresh(ulp)
    # Return full response
    resp = schemas.UserLearningPathResponse.model_validate(ulp, from_attributes=True)
    resp = resp.model_dump()
    resp["learning_path"] = schemas.LearningPathResponse.model_validate(lp, from_attributes=True).model_dump()
    return resp
