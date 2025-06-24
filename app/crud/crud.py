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

def get_users(db: Session, skip: int = 0, limit: int = 100):
    logger.debug(f"Fetching users with skip={skip}, limit={limit}")
    return db.query(models.User).offset(skip).limit(limit).all()

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
# ... Copilot should implement CRUD for other models (ProficiencyLevel, ProjectRole, UserSkill, RoleSkillRequirement, Course, LearningPath, LearningPathCourse, UserLearningPath, UserCourseProgress, AuditLog)
