from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.core.database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = crud.create_course(db, course)
    return db_course

@router.get("/", response_model=List[schemas.CourseResponse])
def get_courses(
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None, description="Search by course name or description"),
    sort_by: str = Query("id", description="Sort by field name"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    return crud.get_courses(db, skip=skip, limit=limit, search=search, sort_by=sort_by, sort_order=sort_order)

@router.get("/{course_id}", response_model=schemas.CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course

@router.put("/{course_id}", response_model=schemas.CourseResponse)
def update_course(course_id: int, course: schemas.CourseUpdate, db: Session = Depends(get_db)):
    db_course = crud.update_course(db, course_id, course)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course

@router.delete("/{course_id}", response_model=schemas.CourseResponse)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.delete_course(db, course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course
