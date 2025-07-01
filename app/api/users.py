from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.api.auth import get_current_admin_user
from app.core.database import get_db
from app.schemas.schemas import PaginatedResponse
import logging

logger = logging.getLogger("lms_backend.api.users")

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

@router.get("/", response_model=PaginatedResponse[schemas.UserResponse])
async def read_all_users(
    db: Annotated[Session, Depends(get_db)],
    current_admin_user: Annotated[models.User, Depends(get_current_admin_user)],
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None, description="Search by user name, email, or SSO ID"),
    sort_by: str = Query("id", description="Sort by field name"),
    sort_order: str = Query("asc", description="Sort order: asc or desc")
):
    logger.debug("Fetching all users with cascading details.")
    try:
        total = crud.count_users(db, search=search)
        users = crud.get_users(db, skip=skip, limit=limit, search=search, sort_by=sort_by, sort_order=sort_order)
        user_list = []
        for user in users:
            user_dict = user.__dict__.copy()
            # Project role
            if getattr(user, "project_role", None):
                user_dict["current_project_role"] = schemas.ProjectRoleResponse.model_validate(user.project_role, from_attributes=True)
            else:
                user_dict["current_project_role"] = None
            # User skills with custom schema (UserSkillDisplay)
            user_dict["user_skills"] = []
            for us in getattr(user, "user_skills", []):
                skill_id = us.skill_id
                skill_name = us.skill.name if us.skill else None
                proficiency_level_id = us.proficiency_level.id if us.proficiency_level else None
                proficiency_level_name = us.proficiency_level.name if us.proficiency_level else None
                user_dict["user_skills"].append({
                    "id": us.id,
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "proficiency_level_id": proficiency_level_id,
                    "proficiency_level_name": proficiency_level_name
                })
            # Assigned learning paths (fully serialize)
            user_dict["user_learning_paths"] = []
            for ulp in getattr(user, "user_learning_paths", []):
                lp_dict = schemas.UserLearningPathResponse.model_validate(ulp, from_attributes=True).model_dump()
                # Eagerly serialize nested learning_path if present
                if hasattr(ulp, "learning_path") and ulp.learning_path:
                    lp_dict["learning_path"] = schemas.LearningPathResponse.model_validate(ulp.learning_path, from_attributes=True).model_dump()
                user_dict["user_learning_paths"].append(lp_dict)
            # Learning progress (fully serialize)
            user_dict["user_course_progress"] = []
            for ucp in getattr(user, "user_course_progress", []):
                cp_dict = schemas.UserCourseProgressResponse.model_validate(ucp, from_attributes=True).model_dump()
                # Eagerly serialize nested course if present
                if hasattr(ucp, "course") and ucp.course:
                    cp_dict["course"] = schemas.CourseResponse.model_validate(ucp.course, from_attributes=True).model_dump()
                user_dict["user_course_progress"].append(cp_dict)
            user_list.append(user_dict)
        logger.info(f"Fetched {len(user_list)} users with cascading details.")
        return {"total": total, "items": user_list}
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
    # Serialize user as in list endpoint
    user = db_user
    user_dict = user.__dict__.copy()
    if getattr(user, "project_role", None):
        user_dict["current_project_role"] = schemas.ProjectRoleResponse.model_validate(user.project_role, from_attributes=True)
    else:
        user_dict["current_project_role"] = None
    user_dict["user_skills"] = []
    for us in getattr(user, "user_skills", []):
        skill_id = us.skill_id
        skill_name = us.skill.name if us.skill else None
        proficiency_level_id = us.proficiency_level.id if us.proficiency_level else None
        proficiency_level_name = us.proficiency_level.name if us.proficiency_level else None
        user_dict["user_skills"].append({
            "id": us.id,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "proficiency_level_id": proficiency_level_id,
            "proficiency_level_name": proficiency_level_name
        })
    user_dict["user_learning_paths"] = []
    for ulp in getattr(user, "user_learning_paths", []):
        lp_dict = schemas.UserLearningPathResponse.model_validate(ulp, from_attributes=True).model_dump()
        if hasattr(ulp, "learning_path") and ulp.learning_path:
            lp_dict["learning_path"] = schemas.LearningPathResponse.model_validate(ulp.learning_path, from_attributes=True).model_dump()
        user_dict["user_learning_paths"].append(lp_dict)
    user_dict["user_course_progress"] = []
    for ucp in getattr(user, "user_course_progress", []):
        cp_dict = schemas.UserCourseProgressResponse.model_validate(ucp, from_attributes=True).model_dump()
        if hasattr(ucp, "course") and ucp.course:
            cp_dict["course"] = schemas.CourseResponse.model_validate(ucp.course, from_attributes=True).model_dump()
        user_dict["user_course_progress"].append(cp_dict)
    logger.info(f"User found: {user.email}")
    return user_dict

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
        # Serialize user as in list endpoint
        user = updated_user
        user_dict = user.__dict__.copy()
        if getattr(user, "project_role", None):
            user_dict["current_project_role"] = schemas.ProjectRoleResponse.model_validate(user.project_role, from_attributes=True)
        else:
            user_dict["current_project_role"] = None
        user_dict["user_skills"] = []
        for us in getattr(user, "user_skills", []):
            skill_id = us.skill_id
            skill_name = us.skill.name if us.skill else None
            proficiency_level_id = us.proficiency_level.id if us.proficiency_level else None
            proficiency_level_name = us.proficiency_level.name if us.proficiency_level else None
            user_dict["user_skills"].append({
                "id": us.id,
                "skill_id": skill_id,
                "skill_name": skill_name,
                "proficiency_level_id": proficiency_level_id,
                "proficiency_level_name": proficiency_level_name
            })
        user_dict["user_learning_paths"] = []
        for ulp in getattr(user, "user_learning_paths", []):
            lp_dict = schemas.UserLearningPathResponse.model_validate(ulp, from_attributes=True).model_dump()
            if hasattr(ulp, "learning_path") and ulp.learning_path:
                lp_dict["learning_path"] = schemas.LearningPathResponse.model_validate(ulp.learning_path, from_attributes=True).model_dump()
            user_dict["user_learning_paths"].append(lp_dict)
        user_dict["user_course_progress"] = []
        for ucp in getattr(user, "user_course_progress", []):
            cp_dict = schemas.UserCourseProgressResponse.model_validate(ucp, from_attributes=True).model_dump()
            if hasattr(ucp, "course") and ucp.course:
                cp_dict["course"] = schemas.CourseResponse.model_validate(ucp.course, from_attributes=True).model_dump()
            user_dict["user_course_progress"].append(cp_dict)
        logger.info(f"User updated: {user.email}")
        return user_dict
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
    # Fetch and serialize user before deletion
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        logger.warning(f"User not found for deletion: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    user = db_user
    user_dict = user.__dict__.copy()
    if getattr(user, "project_role", None):
        user_dict["current_project_role"] = schemas.ProjectRoleResponse.model_validate(user.project_role, from_attributes=True)
    else:
        user_dict["current_project_role"] = None
    user_dict["user_skills"] = []
    for us in getattr(user, "user_skills", []):
        skill_id = us.skill_id
        skill_name = us.skill.name if us.skill else None
        proficiency_level_id = us.proficiency_level.id if us.proficiency_level else None
        proficiency_level_name = us.proficiency_level.name if us.proficiency_level else None
        user_dict["user_skills"].append({
            "id": us.id,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "proficiency_level_id": proficiency_level_id,
            "proficiency_level_name": proficiency_level_name
        })
    user_dict["user_learning_paths"] = []
    for ulp in getattr(user, "user_learning_paths", []):
        lp_dict = schemas.UserLearningPathResponse.model_validate(ulp, from_attributes=True).model_dump()
        if hasattr(ulp, "learning_path") and ulp.learning_path:
            lp_dict["learning_path"] = schemas.LearningPathResponse.model_validate(ulp.learning_path, from_attributes=True).model_dump()
        user_dict["user_learning_paths"].append(lp_dict)
    user_dict["user_course_progress"] = []
    for ucp in getattr(user, "user_course_progress", []):
        cp_dict = schemas.UserCourseProgressResponse.model_validate(ucp, from_attributes=True).model_dump()
        if hasattr(ucp, "course") and ucp.course:
            cp_dict["course"] = schemas.CourseResponse.model_validate(ucp.course, from_attributes=True).model_dump()
        user_dict["user_course_progress"].append(cp_dict)
    # Now delete the user
    crud.delete_user(db, user_id=user_id)
    logger.info(f"User deleted: {user.email}")
    return user_dict

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
        # Serialize response
        return {
            "id": existing_user_skill.id,
            "skill_id": existing_user_skill.skill_id,
            "skill_name": existing_user_skill.skill.name if existing_user_skill.skill else None,
            "proficiency_level_id": existing_user_skill.proficiency_level_id,
            "proficiency_level_name": existing_user_skill.proficiency_level.name if existing_user_skill.proficiency_level else None
        }
    else:
        logger.info(f"Adding new skill for user ID {user_id}: {user_skill.skill_id}")
        new_user_skill = models.UserSkill(**user_skill.dict())
        db.add(new_user_skill)
        db.commit()
        db.refresh(new_user_skill)
        # Serialize response
        return {
            "id": new_user_skill.id,
            "skill_id": new_user_skill.skill_id,
            "skill_name": new_user_skill.skill.name if new_user_skill.skill else None,
            "proficiency_level_id": new_user_skill.proficiency_level_id,
            "proficiency_level_name": new_user_skill.proficiency_level.name if new_user_skill.proficiency_level else None
        }
