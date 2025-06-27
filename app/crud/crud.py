from sqlalchemy.orm import Session
import app.models.models as models
import app.schemas.schemas as schemas
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("lms_backend.crud")

def hash_password(password: str):
    logger.debug("Hashing password.")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    logger.debug("Verifying password.")
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    logger.debug("Creating access token.")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_sso_id(db: Session, sso_id: str):
    logger.debug(f"Fetching user by SSO ID: {sso_id}")
    return db.query(models.User).filter(models.User.sso_id == sso_id).first()

def get_user(db: Session, user_id: int):
    logger.debug(f"Fetching user by ID: {user_id}")
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100, search=None, sort_by="id", sort_order="asc"):
    logger.debug(f"Fetching users with skip={skip}, limit={limit}, search={search}, sort_by={sort_by}, sort_order={sort_order}")
    query = db.query(models.User)
    if search:
        query = query.filter(
            (models.User.first_name.ilike(f"%{search}%")) |
            (models.User.last_name.ilike(f"%{search}%")) |
            (models.User.email.ilike(f"%{search}%")) |
            (models.User.sso_id.ilike(f"%{search}%"))
        )
    if sort_order == "desc":
        query = query.order_by(getattr(models.User, sort_by).desc())
    else:
        query = query.order_by(getattr(models.User, sort_by).asc())
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    logger.debug(f"Creating user: {user.email}")
    hashed_password = hash_password(user.password)
    db_user = models.User(
        sso_id=user.sso_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
        role="Developer"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    logger.debug(f"Updating user ID: {user_id}")
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        update_data = user.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    logger.debug(f"Deleting user ID: {user_id}")
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_skill_by_name(db: Session, skill_name: str):
    logger.debug(f"Fetching skill by name: {skill_name}")
    return db.query(models.Skill).filter(models.Skill.name == skill_name).first()

def get_skill(db: Session, skill_id: int):
    logger.debug(f"Fetching skill by ID: {skill_id}")
    return db.query(models.Skill).filter(models.Skill.id == skill_id).first()

def get_skills(db: Session, skip: int = 0, limit: int = 100):
    logger.debug(f"Fetching skills with skip={skip}, limit={limit}")
    return db.query(models.Skill).offset(skip).limit(limit).all()

def create_skill(db: Session, skill: schemas.SkillCreate):
    logger.debug(f"Creating skill: {skill.name}")
    db_skill = models.Skill(name=skill.name, description=skill.description)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

def get_project_role_by_name(db: Session, role_name: str):
    logger.debug(f"Fetching project role by name: {role_name}")
    return db.query(models.ProjectRole).filter(models.ProjectRole.name == role_name).first()

def get_proficiency_level_by_level(db: Session, level: int):
    logger.debug(f"Fetching proficiency level by level: {level}")
    return db.query(models.ProficiencyLevel).filter(models.ProficiencyLevel.id == level).first()

def create_user_with_role(db: Session, user):
    logger.debug(f"Creating user with role: {user.email}")
    hashed_password = hash_password(user.password)
    db_user = models.User(
        sso_id=user.sso_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
        role="Developer",
        current_project_role_id=user.current_project_role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def upsert_user_skill(db: Session, user_id: int, skill_id: int, proficiency_level_id: int):
    logger.debug(f"Upserting user skill: user_id={user_id}, skill_id={skill_id}, proficiency_level_id={proficiency_level_id}")
    user_skill = db.query(models.UserSkill).filter_by(user_id=user_id, skill_id=skill_id).first()
    if user_skill:
        user_skill.proficiency_level_id = proficiency_level_id
        db.add(user_skill)
    else:
        user_skill = models.UserSkill(user_id=user_id, skill_id=skill_id, proficiency_level_id=proficiency_level_id)
        db.add(user_skill)
    db.commit()
    db.refresh(user_skill)
    return user_skill

# COURSE CRUD

def create_course(db, course: schemas.CourseCreate):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_courses(db, skip=0, limit=100, search=None, sort_by="id", sort_order="asc"):
    query = db.query(models.Course)
    if search:
        query = query.filter(
            (models.Course.name.ilike(f"%{search}%")) |
            (models.Course.description.ilike(f"%{search}%"))
        )
    if sort_order == "desc":
        query = query.order_by(getattr(models.Course, sort_by).desc())
    else:
        query = query.order_by(getattr(models.Course, sort_by).asc())
    return query.offset(skip).limit(limit).all()

def get_course(db, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()

def update_course(db, course_id: int, course: schemas.CourseUpdate):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        return None
    for k, v in course.dict(exclude_unset=True).items():
        setattr(db_course, k, v)
    db.commit()
    db.refresh(db_course)
    return db_course

def delete_course(db, course_id: int):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        return None
    db.delete(db_course)
    db.commit()
    return db_course

# LEARNING PATH CRUD

def create_learning_path_with_courses(db, lp: schemas.LearningPathCreate):
    db_lp = models.LearningPath(**lp.dict(exclude={"courses"}))
    db.add(db_lp)
    db.commit()
    db.refresh(db_lp)
    # Add courses
    for course_id in getattr(lp, "courses", []):
        db_lpc = models.LearningPathCourse(learning_path_id=db_lp.id, course_id=course_id)
        db.add(db_lpc)
    db.commit()
    db.refresh(db_lp)
    return get_learning_path_with_details(db, db_lp.id)

def get_learning_paths_with_details(db, skip=0, limit=100, search=None, sort_by="id", sort_order="asc"):
    query = db.query(models.LearningPath)
    if search:
        query = query.filter(
            (models.LearningPath.name.ilike(f"%{search}%")) |
            (models.LearningPath.description.ilike(f"%{search}%"))
        )
    if sort_order == "desc":
        query = query.order_by(getattr(models.LearningPath, sort_by).desc())
    else:
        query = query.order_by(getattr(models.LearningPath, sort_by).asc())
    lps = query.offset(skip).limit(limit).all()
    return [get_learning_path_with_details(db, lp.id) for lp in lps]

def get_learning_path_with_details(db, learning_path_id: int):
    lp = db.query(models.LearningPath).filter(models.LearningPath.id == learning_path_id).first()
    if not lp:
        return None
    # Build response with all associated courses and their details
    courses = []
    for lpc in lp.learning_path_courses:
        course = lpc.course
        if course:
            course_data = schemas.CourseResponse.model_validate(course, from_attributes=True).model_dump()
            lpc_dict = schemas.LearningPathCourseResponse.model_validate(lpc, from_attributes=True).model_dump()
            lpc_dict["course"] = course_data
            courses.append(lpc_dict)
    lp_dict = schemas.LearningPathResponse.model_validate(lp, from_attributes=True).model_dump()
    lp_dict["courses"] = courses
    return lp_dict

def update_learning_path_with_courses(db, learning_path_id: int, lp: schemas.LearningPathCreate):
    db_lp = db.query(models.LearningPath).filter(models.LearningPath.id == learning_path_id).first()
    if not db_lp:
        return None
    for k, v in lp.dict(exclude_unset=True, exclude={"courses"}).items():
        setattr(db_lp, k, v)
    # Remove old courses
    db.query(models.LearningPathCourse).filter(models.LearningPathCourse.learning_path_id == learning_path_id).delete()
    db.commit()
    # Add new courses
    for course_id in getattr(lp, "courses", []):
        db_lpc = models.LearningPathCourse(learning_path_id=learning_path_id, course_id=course_id)
        db.add(db_lpc)
    db.commit()
    db.refresh(db_lp)
    return get_learning_path_with_details(db, learning_path_id)

def delete_learning_path(db, learning_path_id: int):
    db_lp = db.query(models.LearningPath).filter(models.LearningPath.id == learning_path_id).first()
    if not db_lp:
        return None
    db.delete(db_lp)
    db.commit()
    return db_lp
