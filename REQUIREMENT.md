# Project: Account-Specific Learning Management System (LMS) - Backend API Development

## Overall Goal:
Develop a robust, scalable, and secure backend API for the Account-Specific Learning Management System. This API will handle data persistence (MySQL), business logic, skill gap calculations, learning recommendations, and serve data to the frontend.

## Development Environment:
- **IDE:** VS Code
- **AI Tool:** GitHub Copilot Agent
- **Backend Framework:** Python (FastAPI) - Preferred for performance, modern features, and automatic OpenAPI documentation.
- **Database:** MySQL
- **ORM:** SQLAlchemy (for database interactions)
- **Database Connector:** `mysql-connector-python` or `pymysql`
- **Authentication:** JWT (JSON Web Tokens) for API security, with a placeholder for future SSO integration.
- **Excel Processing:** `pandas` library for handling Excel file uploads.

## Detailed Development Plan for GitHub Copilot Agent:

---

### **Phase 1: Project Setup & Database Foundation**

**Task 1.1: Initialize Python Project, Virtual Environment, and Install Core Packages**
- **Action:** Set up a new Python project directory, create a virtual environment, and install all necessary Python packages.
- **Instructions:**
    1.  **Create project directory (if not already):** `mkdir lms-backend`
    2.  **Run in terminal:** `cd lms-backend`
    3.  **Create virtual environment:** `python -m venv venv`
    4.  **Activate virtual environment:**
        * On Windows: `.\venv\Scripts\activate`
        * On macOS/Linux: `source venv/bin/activate`
    5.  **Install core packages:**
        ```bash
        pip install fastapi uvicorn "python-multipart[standard]" sqlalchemy mysql-connector-python bcrypt python-jose[cryptography] pandas openpyxl
        ```
        * `fastapi`: Web framework.
        * `uvicorn`: ASGI server for running FastAPI.
        * `python-multipart`: For handling form data and file uploads.
        * `sqlalchemy`: Python SQL toolkit and Object Relational Mapper.
        * `mysql-connector-python`: MySQL database connector.
        * `bcrypt`: For password hashing.
        * `python-jose[cryptography]`: For JWT (JSON Web Tokens).
        * `pandas`: For data manipulation, especially Excel processing.
        * `openpyxl`: Backend for `pandas` to read/write `.xlsx` files.
    6.  **Create main application file:** `touch main.py`
    7.  **Create initial `main.py` content (basic FastAPI app):**
        ```python
        from fastapi import FastAPI

        app = FastAPI(title="LMS Backend API", version="1.0.0")

        @app.get("/")
        async def root():
            return {"message": "LMS Backend API is running!"}

        if __name__ == "__main__":
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
        ```
    8.  **Create `.env` file for environment variables (e.g., database credentials, secret key):**
        ```
        DATABASE_URL="mysql+mysqlconnector://user:password@host:port/dbname"
        SECRET_KEY="your_super_secret_key_here"
        ALGORITHM="HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        ```
    9.  **Create a `config.py` to load environment variables:**
        ```python
        import os
        from dotenv import load_dotenv

        load_dotenv() # take environment variables from .env.

        DATABASE_URL = os.getenv("DATABASE_URL")
        SECRET_KEY = os.getenv("SECRET_KEY")
        ALGORITHM = os.getenv("ALGORITHM", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

        # Ensure SECRET_KEY is set
        if not SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable not set. Please set it in .env file.")
        ```
    10. **Add `config.py` import to `main.py` (ensure `config.py` is created before `main.py` is edited).**

**Task 1.2: Define MySQL Database Schema using SQLAlchemy Models**
- **Action:** Translate the previously designed MySQL schema into SQLAlchemy ORM models.
- **Instructions:**
    1.  **Create a `database.py` file to handle database connection and session management:**
        ```python
        from sqlalchemy import create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from config import DATABASE_URL

        # Use mysql+mysqlconnector for the connection string
        # Example: DATABASE_URL="mysql+mysqlconnector://user:password@host:port/dbname"
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()

        # Dependency to get DB session
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        ```
    2.  **Create a `models.py` file for SQLAlchemy ORM models based on the schema design:**
        * `users`
        * `skills`
        * `proficiency_levels`
        * `user_skills`
        * `project_roles`
        * `role_skill_requirements`
        * `courses`
        * `learning_paths`
        * `learning_path_courses`
        * `user_learning_paths`
        * `user_course_progress`
        * `audit_logs`
        * **Ensure relationships (Foreign Keys) are correctly defined using SQLAlchemy's `relationship` and `ForeignKey`.**
        * **Example for `users` and `skills` (Copilot should expand for all):**
            ```python
            from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
            from sqlalchemy.orm import relationship
            from sqlalchemy.sql import func
            from database import Base

            class User(Base):
                __tablename__ = "users"
                id = Column(Integer, primary_key=True, index=True)
                sso_id = Column(String(255), unique=True, index=True, nullable=False)
                email = Column(String(255), unique=True, index=True, nullable=False)
                first_name = Column(String(255), nullable=False)
                last_name = Column(String(255), nullable=False)
                hashed_password = Column(String(255), nullable=False) # For local login if SSO fails or for internal admins
                role = Column(String(50), default="Developer", nullable=False) # "Admin", "Developer"
                current_project_role_id = Column(Integer, ForeignKey("project_roles.id"), nullable=True)
                date_joined = Column(DateTime(timezone=True), server_default=func.now())
                last_login = Column(DateTime(timezone=True), onupdate=func.now())

                project_role = relationship("ProjectRole", back_populates="users")
                user_skills = relationship("UserSkill", back_populates="user")
                user_learning_paths = relationship("UserLearningPath", back_populates="user")
                user_course_progress = relationship("UserCourseProgress", back_populates="user")
                audit_logs = relationship("AuditLog", back_populates="admin_user")

            class Skill(Base):
                __tablename__ = "skills"
                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(255), unique=True, index=True, nullable=False)
                description = Column(Text, nullable=True)

                user_skills = relationship("UserSkill", back_populates="skill")
                role_skill_requirements = relationship("RoleSkillRequirement", back_populates="skill")
                courses = relationship("Course", back_populates="skill")

            # ... Copilot should generate other models here (ProficiencyLevel, ProjectRole, UserSkill, RoleSkillRequirement, Course, LearningPath, LearningPathCourse, UserLearningPath, UserCourseProgress, AuditLog)
            # Ensure proper Foreign Keys and relationships are defined.

            class ProficiencyLevel(Base):
                __tablename__ = "proficiency_levels"
                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(50), unique=True, nullable=False)
                description = Column(Text, nullable=True)

            class ProjectRole(Base):
                __tablename__ = "project_roles"
                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(255), unique=True, nullable=False)
                description = Column(Text, nullable=True)

                users = relationship("User", back_populates="project_role")
                role_skill_requirements = relationship("RoleSkillRequirement", back_populates="project_role")

            class UserSkill(Base):
                __tablename__ = "user_skills"
                id = Column(Integer, primary_key=True, index=True)
                user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
                skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
                proficiency_level_id = Column(Integer, ForeignKey("proficiency_levels.id"), nullable=False)
                last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

                user = relationship("User", back_populates="user_skills")
                skill = relationship("Skill", back_populates="user_skills")
                proficiency_level = relationship("ProficiencyLevel") # No back_populates needed if not needed from ProficiencyLevel side

            class RoleSkillRequirement(Base):
                __tablename__ = "role_skill_requirements"
                id = Column(Integer, primary_key=True, index=True)
                project_role_id = Column(Integer, ForeignKey("project_roles.id"), nullable=False)
                skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
                min_proficiency_level_id = Column(Integer, ForeignKey("proficiency_levels.id"), nullable=False)
                is_mandatory = Column(Boolean, default=True, nullable=False)

                project_role = relationship("ProjectRole", back_populates="role_skill_requirements")
                skill = relationship("Skill", back_populates="role_skill_requirements")
                min_proficiency_level = relationship("ProficiencyLevel")

            class Course(Base):
                __tablename__ = "courses"
                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(255), unique=True, nullable=False)
                description = Column(Text, nullable=True)
                provider = Column(String(255), nullable=True)
                duration_hours = Column(Integer, nullable=True)
                skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True) # Primary skill covered
                recommended_proficiency_level_id = Column(Integer, ForeignKey("proficiency_levels.id"), nullable=True)
                image_url = Column(String(255), nullable=True) # For pictorial representation

                skill = relationship("Skill", back_populates="courses")
                recommended_proficiency_level = relationship("ProficiencyLevel")
                learning_path_courses = relationship("LearningPathCourse", back_populates="course")
                user_course_progress = relationship("UserCourseProgress", back_populates="course")

            class LearningPath(Base):
                __tablename__ = "learning_paths"
                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(255), unique=True, nullable=False)
                description = Column(Text, nullable=True)

                learning_path_courses = relationship("LearningPathCourse", back_populates="learning_path")
                user_learning_paths = relationship("UserLearningPath", back_populates="learning_path")

            class LearningPathCourse(Base):
                __tablename__ = "learning_path_courses"
                id = Column(Integer, primary_key=True, index=True)
                learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
                course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
                sequence_order = Column(Integer, nullable=False)

                learning_path = relationship("LearningPath", back_populates="learning_path_courses")
                course = relationship("Course", back_populates="learning_path_courses")

            class UserLearningPath(Base):
                __tablename__ = "user_learning_paths"
                id = Column(Integer, primary_key=True, index=True)
                user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
                learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
                assigned_date = Column(DateTime(timezone=True), server_default=func.now())
                status = Column(String(50), default="Assigned", nullable=False) # e.g., 'Assigned', 'Registered', 'In Progress', 'Completed'
                completion_date = Column(DateTime(timezone=True), nullable=True)
                is_mandatory_by_system = Column(Boolean, default=False, nullable=False) # From system recommendation
                is_registered_by_developer = Column(Boolean, default=False, nullable=False) # For optional courses registered by user

                user = relationship("User", back_populates="user_learning_paths")
                learning_path = relationship("LearningPath", back_populates="user_learning_paths")

            class UserCourseProgress(Base):
                __tablename__ = "user_course_progress"
                id = Column(Integer, primary_key=True, index=True)
                user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
                course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
                status = Column(String(50), default="Not Started", nullable=False) # 'Not Started', 'In Progress', 'Completed'
                progress_percentage = Column(Integer, default=0, nullable=False) # 0-100
                last_accessed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
                completion_date = Column(DateTime(timezone=True), nullable=True)

                user = relationship("User", back_populates="user_course_progress")
                course = relationship("Course", back_populates="user_course_progress")

            class AuditLog(Base):
                __tablename__ = "audit_logs"
                id = Column(Integer, primary_key=True, index=True)
                admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
                action = Column(String(255), nullable=False) # e.g., 'Changed Role', 'Uploaded Skill Matrix', 'Assigned Course'
                details = Column(Text, nullable=True) # JSON or text for specific changes
                timestamp = Column(DateTime(timezone=True), server_default=func.now())

                admin_user = relationship("User", back_populates="audit_logs")
            ```
    3.  **Update `main.py` to create database tables on startup (for development purposes):**
        ```python
        from fastapi import FastAPI
        from database import engine, Base # Import Base and engine
        import models # Import your models file to register them with Base

        # Create all database tables
        Base.metadata.create_all(bind=engine)

        app = FastAPI(title="LMS Backend API", version="1.0.0")

        @app.get("/")
        async def root():
            return {"message": "LMS Backend API is running!"}

        # Add your API routes here

        if __name__ == "__main__":
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
        ```
    4.  **Before running, ensure your MySQL server is running and accessible with the credentials specified in `.env`.**

**Task 1.3: Create Pydantic Schemas (Request/Response Models)**
- **Action:** Define Pydantic schemas for data validation and serialization. These will be used for API request bodies and response models.
- **Instructions:**
    1.  **Create a `schemas.py` file:**
        * Define Pydantic models for:
            * `UserCreate`, `UserUpdate`, `UserResponse` (for Admin and Developer views, potentially `UserBase` for common fields).
            * `SkillCreate`, `SkillResponse`
            * `ProficiencyLevelCreate`, `ProficiencyLevelResponse`
            * `ProjectRoleCreate`, `ProjectRoleResponse`
            * `UserSkillCreate`, `UserSkillResponse`
            * `RoleSkillRequirementCreate`, `RoleSkillRequirementResponse`
            * `CourseCreate`, `CourseUpdate`, `CourseResponse`
            * `LearningPathCreate`, `LearningPathResponse`
            * `LearningPathCourseCreate`, `LearningPathCourseResponse`
            * `UserLearningPathCreate`, `UserLearningPathUpdate`, `UserLearningPathResponse`
            * `UserCourseProgressCreate`, `UserCourseProgressUpdate`, `UserCourseProgressResponse`
            * `Token` (for JWT)
            * `TokenData` (for JWT)
            * `LoginRequest`
            * `ExcelUploadResponse` (for skill matrix upload)
            * `SkillGapReportResponse`
            * `LaggingProgressReportResponse`
            * `ComplianceReportResponse`
        * **Example for `User` and `Skill` (Copilot should expand for others):**
            ```python
            from pydantic import BaseModel, EmailStr
            from typing import List, Optional
            from datetime import datetime

            class Token(BaseModel):
                access_token: str
                token_type: str

            class TokenData(BaseModel):
                username: Optional[str] = None # Using sso_id as username for JWT subject

            class UserBase(BaseModel):
                email: EmailStr
                first_name: str
                last_name: str

            class UserCreate(UserBase):
                sso_id: str
                password: str # This would be sent for local login, or managed by SSO

            class UserUpdate(BaseModel):
                email: Optional[EmailStr] = None
                first_name: Optional[str] = None
                last_name: Optional[str] = None
                role: Optional[str] = None
                current_project_role_id: Optional[int] = None

            class SkillBase(BaseModel):
                name: str
                description: Optional[str] = None

            class SkillCreate(SkillBase):
                pass

            class ProficiencyLevelBase(BaseModel):
                name: str
                description: Optional[str] = None

            class ProficiencyLevelCreate(ProficiencyLevelBase):
                pass

            class ProjectRoleBase(BaseModel):
                name: str
                description: Optional[str] = None

            class ProjectRoleCreate(ProjectRoleBase):
                pass

            class UserSkillBase(BaseModel):
                user_id: int
                skill_id: int
                proficiency_level_id: int

            class UserSkillCreate(UserSkillBase):
                pass

            class RoleSkillRequirementBase(BaseModel):
                project_role_id: int
                skill_id: int
                min_proficiency_level_id: int
                is_mandatory: bool = True

            class RoleSkillRequirementCreate(RoleSkillRequirementBase):
                pass

            class CourseBase(BaseModel):
                name: str
                description: Optional[str] = None
                provider: Optional[str] = None
                duration_hours: Optional[int] = None
                skill_id: Optional[int] = None
                recommended_proficiency_level_id: Optional[int] = None
                image_url: Optional[str] = None

            class CourseCreate(CourseBase):
                pass

            class CourseUpdate(BaseModel):
                name: Optional[str] = None
                description: Optional[str] = None
                provider: Optional[str] = None
                duration_hours: Optional[int] = None
                skill_id: Optional[int] = None
                recommended_proficiency_level_id: Optional[int] = None
                image_url: Optional[str] = None

            class LearningPathBase(BaseModel):
                name: str
                description: Optional[str] = None

            class LearningPathCreate(LearningPathBase):
                pass

            class LearningPathCourseBase(BaseModel):
                learning_path_id: int
                course_id: int
                sequence_order: int

            class LearningPathCourseCreate(LearningPathCourseBase):
                pass

            class UserLearningPathBase(BaseModel):
                user_id: int
                learning_path_id: int
                assigned_date: Optional[datetime] = None
                status: str = "Assigned"
                completion_date: Optional[datetime] = None
                is_mandatory_by_system: bool = False
                is_registered_by_developer: bool = False

            class UserLearningPathCreate(UserLearningPathBase):
                pass

            class UserLearningPathUpdate(BaseModel):
                status: Optional[str] = None
                completion_date: Optional[datetime] = None

            class UserCourseProgressBase(BaseModel):
                user_id: int
                course_id: int
                status: str = "Not Started"
                progress_percentage: int = 0
                last_accessed: Optional[datetime] = None
                completion_date: Optional[datetime] = None

            class UserCourseProgressCreate(UserCourseProgressBase):
                pass

            class UserCourseProgressUpdate(BaseModel):
                status: Optional[str] = None
                progress_percentage: Optional[int] = None
                last_accessed: Optional[datetime] = None
                completion_date: Optional[datetime] = None

            class AuditLogBase(BaseModel):
                admin_user_id: int
                action: str
                details: Optional[str] = None
                timestamp: Optional[datetime] = None

            class AuditLogCreate(AuditLogBase):
                pass

            # --- Response Models (Include Relationships where needed) ---
            class SkillResponse(SkillBase):
                id: int
                class Config:
                    orm_mode = True

            class ProficiencyLevelResponse(ProficiencyLevelBase):
                id: int
                class Config:
                    orm_mode = True

            class ProjectRoleResponse(ProjectRoleBase):
                id: int
                class Config:
                    orm_mode = True

            class UserSkillResponse(UserSkillBase):
                id: int
                skill: SkillResponse # Include related skill data
                proficiency_level: ProficiencyLevelResponse # Include related proficiency level data
                class Config:
                    orm_mode = True

            class RoleSkillRequirementResponse(RoleSkillRequirementBase):
                id: int
                skill: SkillResponse
                min_proficiency_level: ProficiencyLevelResponse
                class Config:
                    orm_mode = True

            class UserResponse(UserBase):
                id: int
                sso_id: str
                role: str
                current_project_role: Optional[ProjectRoleResponse] = None # Include related project role
                date_joined: datetime
                last_login: Optional[datetime] = None
                user_skills: List[UserSkillResponse] = [] # Include user's skills
                class Config:
                    orm_mode = True

            class CourseResponse(CourseBase):
                id: int
                skill: Optional[SkillResponse] = None
                recommended_proficiency_level: Optional[ProficiencyLevelResponse] = None
                class Config:
                    orm_mode = True

            class LearningPathCourseResponse(LearningPathCourseBase):
                id: int
                course: CourseResponse
                class Config:
                    orm_mode = True

            class LearningPathResponse(LearningPathBase):
                id: int
                courses: List[LearningPathCourseResponse] = []
                class Config:
                    orm_mode = True

            class UserLearningPathResponse(UserLearningPathBase):
                id: int
                learning_path: LearningPathResponse
                class Config:
                    orm_mode = True

            class UserCourseProgressResponse(UserCourseProgressBase):
                id: int
                course: CourseResponse
                class Config:
                    orm_mode = True

            class AuditLogResponse(AuditLogBase):
                id: int
                class Config:
                    orm_mode = True

            # Request/Response models for specific features
            class ExcelUploadResponse(BaseModel):
                message: str
                details: dict

            class SkillGapItem(BaseModel):
                developer_id: int
                developer_name: str
                role_name: str
                required_skill: str
                required_proficiency: str
                current_proficiency: str
                gap_identified: bool

            class SkillGapReportResponse(BaseModel):
                report_date: datetime
                skill_gaps: List[SkillGapItem]

            class LaggingProgressItem(BaseModel):
                user_id: int
                user_name: str
                course_name: str
                progress_percentage: int
                status: str
                assigned_date: datetime
                days_lagging: int

            class LaggingProgressReportResponse(BaseModel):
                report_date: datetime
                lagging_individuals: List[LaggingProgressItem]

            class ComplianceReportItem(BaseModel):
                designation: str
                total_assigned: int
                completed: int
                compliance_percentage: float

            class ComplianceReportResponse(BaseModel):
                report_date: datetime
                compliance_data: List[ComplianceReportItem]

            class LoginRequest(BaseModel):
                username: str # This will be SSO ID or email
                password: str

            class RoleSkillSwapSuggestion(BaseModel):
                employee_a_id: int
                employee_a_name: str
                employee_a_current_role: str
                employee_b_id: int
                employee_b_name: str
                employee_b_current_role: str
                suggested_swap_benefit: str
                skill_gaps_reduced: List[str]
            ```

---

### **Phase 2: Core API Endpoints (Admin Features)**

**Task 2.1: Authentication Endpoints (Login, Token Generation)**
- **Action:** Implement endpoints for user login, token generation (JWT), and a dependency for protecting routes.
- **Instructions:**
    1.  **Create a `crud.py` file to handle database operations (e.g., `get_user_by_sso_id`, `create_user`, `get_skill_by_name`, etc.):**
        ```python
        from sqlalchemy.orm import Session
        import models, schemas
        from datetime import datetime, timedelta
        from passlib.context import CryptContext
        from jose import JWTError, jwt
        from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # --- Password Hashing ---
        def hash_password(password: str):
            return pwd_context.hash(password)

        def verify_password(plain_password: str, hashed_password: str):
            return pwd_context.verify(plain_password, hashed_password)

        # --- JWT Token Functions ---
        def create_access_token(data: dict):
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt

        # --- User CRUD Operations ---
        def get_user_by_sso_id(db: Session, sso_id: str):
            return db.query(models.User).filter(models.User.sso_id == sso_id).first()

        def get_user(db: Session, user_id: int):
            return db.query(models.User).filter(models.User.id == user_id).first()

        def get_users(db: Session, skip: int = 0, limit: int = 100):
            return db.query(models.User).offset(skip).limit(limit).all()

        def create_user(db: Session, user: schemas.UserCreate):
            hashed_password = hash_password(user.password)
            db_user = models.User(
                sso_id=user.sso_id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                hashed_password=hashed_password,
                role="Developer" # Default role
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user

        def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
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
            db_user = db.query(models.User).filter(models.User.id == user_id).first()
            if db_user:
                db.delete(db_user)
                db.commit()
            return db_user

        # --- Skill CRUD Operations ---
        def get_skill_by_name(db: Session, skill_name: str):
            return db.query(models.Skill).filter(models.Skill.name == skill_name).first()

        def get_skill(db: Session, skill_id: int):
            return db.query(models.Skill).filter(models.Skill.id == skill_id).first()

        def get_skills(db: Session, skip: int = 0, limit: int = 100):
            return db.query(models.Skill).offset(skip).limit(limit).all()

        def create_skill(db: Session, skill: schemas.SkillCreate):
            db_skill = models.Skill(name=skill.name, description=skill.description)
            db.add(db_skill)
            db.commit()
            db.refresh(db_skill)
            return db_skill

        # ... Copilot should implement CRUD for other models (ProficiencyLevel, ProjectRole, UserSkill, RoleSkillRequirement, Course, LearningPath, LearningPathCourse, UserLearningPath, UserCourseProgress, AuditLog)
        # These functions will be called by your API endpoints.
        ```
    2.  **Add Authentication Routes to `main.py`:**
        ```python
        from fastapi import FastAPI, Depends, HTTPException, status
        from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
        from sqlalchemy.orm import Session
        from datetime import timedelta

        import models, schemas, crud # Assuming you've created crud.py
        from database import engine, Base, get_db
        from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY # From config.py
        from jose import JWTError, jwt
        from typing import Annotated

        # Create all database tables (Moved this up from Task 1.2 for clarity)
        Base.metadata.create_all(bind=engine)

        app = FastAPI(title="LMS Backend API", version="1.0.0")

        # OAuth2 scheme for token authentication
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

        def authenticate_user(db: Session, username: str, password: str):
            """Authenticates user based on SSO ID and password."""
            user = crud.get_user_by_sso_id(db, sso_id=username)
            if not user or not crud.verify_password(password, user.hashed_password):
                return False
            return user

        def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
            """Creates a JWT access token."""
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt

        async def get_current_user(
            token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]
        ):
            """Dependency to get the current authenticated user."""
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                sso_id: str = payload.get("sub")
                if sso_id is None:
                    raise credentials_exception
                token_data = schemas.TokenData(username=sso_id)
            except JWTError:
                raise credentials_exception
            user = crud.get_user_by_sso_id(db, sso_id=token_data.username)
            if user is None:
                raise credentials_exception
            return user

        def get_current_admin_user(current_user: Annotated[models.User, Depends(get_current_user)]):
            """Dependency to get the current authenticated Admin user."""
            if current_user.role != "Admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to perform this action. Admin access required."
                )
            return current_user

        # --- Authentication Endpoints ---
        @app.post("/token", response_model=schemas.Token)
        async def login_for_access_token(
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]
        ):
            user = authenticate_user(db, form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.sso_id}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}

        @app.get("/users/me/", response_model=schemas.UserResponse)
        async def read_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
            """Get current authenticated user's details."""
            return current_user

        @app.get("/admin/me/", response_model=schemas.UserResponse)
        async def read_admin_me(current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]):
            """Get current authenticated Admin user's details."""
            return current_admin_user

        # Test endpoint
        @app.get("/")
        async def root():
            return {"message": "LMS Backend API is running!"}
        ```

**Task 2.2: Admin User Management Endpoints**
- **Action:** Implement CRUD APIs for managing users by administrators (change role, skill requirements).
- **Instructions:**
    1.  **Add the following endpoints to `main.py`:**
        * `GET /admin/users/` (Get all users, requires admin)
        * `POST /admin/users/` (Create a new user, requires admin) - mainly for initial setup/internal users, actual SSO managed externally.
        * `GET /admin/users/{user_id}` (Get user by ID, requires admin)
        * `PUT /admin/users/{user_id}` (Update user details, including role and current project role, requires admin)
        * `DELETE /admin/users/{user_id}` (Delete user, requires admin)
        * `POST /admin/users/{user_id}/skills` (Manually add/update a user's skill and proficiency, requires admin)
    2.  **Ensure all these endpoints use `Depends(get_current_admin_user)` for authorization.**
    3.  **Example for getting all users and updating a user:**
        ```python
        # In main.py
        from typing import List, Optional
        from fastapi import UploadFile, File

        @app.get("/admin/users/", response_model=List[schemas.UserResponse])
        async def read_all_users(
            skip: int = 0, limit: int = 100,
            db: Annotated[Session, Depends(get_db)],
            current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
        ):
            """Get a list of all users. Requires Admin access."""
            users = crud.get_users(db, skip=skip, limit=limit)
            return users

        @app.post("/admin/users/", response_model=schemas.UserResponse)
        async def create_new_user(
            user: schemas.UserCreate,
            db: Annotated[Session, Depends(get_db)],
            current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
        ):
            """Create a new user. Requires Admin access."""
            db_user = crud.get_user_by_sso_id(db, sso_id=user.sso_id)
            if db_user:
                raise HTTPException(status_code=400, detail="SSO ID already registered")
            return crud.create_user(db=db, user=user)

        @app.put("/admin/users/{user_id}", response_model=schemas.UserResponse)
        async def update_existing_user(
            user_id: int,
            user_update: schemas.UserUpdate,
            db: Annotated[Session, Depends(get_db)],
            current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
        ):
            """Update user details including role and project role. Requires Admin access."""
            db_user = crud.get_user(db, user_id=user_id)
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return crud.update_user(db=db, user_id=user_id, user=user_update)

        @app.post("/admin/users/{user_id}/skills", response_model=schemas.UserSkillResponse)
        async def add_user_skill(
            user_id: int,
            user_skill: schemas.UserSkillCreate,
            db: Annotated[Session, Depends(get_db)],
            current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
        ):
            """Manually add or update a user's skill and proficiency. Requires Admin access."""
            # Ensure user exists
            db_user = crud.get_user(db, user_id=user_id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            # Ensure skill and proficiency level exist
            db_skill = crud.get_skill(db, skill_id=user_skill.skill_id)
            if not db_skill:
                raise HTTPException(status_code=404, detail="Skill not found")
            db_proficiency = crud.get_proficiency_level(db, proficiency_level_id=user_skill.proficiency_level_id)
            if not db_proficiency:
                raise HTTPException(status_code=404, detail="Proficiency level not found")

            # Check if skill already exists for user and update, otherwise create new
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
        ```
    4.  **Update `crud.py` to include `get_proficiency_level` and `update_user` logic.**

**Task 2.3: Skill & Role Matrix Management Endpoints (Manual & Excel Upload)**
- **Action:** Implement CRUD for skills, proficiency levels, project roles, and role-skill requirements. Add an endpoint for Excel file upload to process role-skill matrix data.
- **Instructions:**
    1.  **Add comprehensive CRUD endpoints for `skills`, `proficiency_levels`, and `project_roles` to `main.py`, requiring `get_current_admin_user`.**
    2.  **Implement CRUD for `role_skill_requirements`.**
    3.  **Implement the Excel upload endpoint:**
        * **Endpoint:** `POST /admin/upload-skill-matrix/`
        * **Accepts:** `UploadFile` (Excel file).
        * **Logic:**
            * Read the Excel file using `pandas`.
            * Parse the relevant sheets (e.g., one for skills, one for roles, one for role-skill mappings).
            * Validate data.
            * Update/create `Skill`, `ProficiencyLevel`, `ProjectRole`, and `RoleSkillRequirement` records in the database.
            * Handle errors (e.g., invalid format, missing data).
            * Return a success/failure message with details.
        * **Example Excel structure hints for Copilot:**
            * **Sheet: "Skills"** -> Columns: `Skill Name`, `Description`
            * **Sheet: "Proficiency Levels"** -> Columns: `Level Name`, `Description`
            * **Sheet: "Project Roles"** -> Columns: `Role Name`, ` `Description`
            * **Sheet: "Role Skill Matrix"** -> Columns: `Role Name`, `Skill Name`, `Min Proficiency Level Name`, `Is Mandatory (Yes/No)`
        * **Add `read_excel_file` utility function in a new `utils.py` for `pandas` operations.**
    4.  **Example Excel upload endpoint in `main.py`:**
        ```python
        # In main.py
        import pandas as pd
        from io import BytesIO
        from utils import parse_excel_skill_matrix # Assuming parse_excel_skill_matrix in utils.py

        @app.post("/admin/upload-skill-matrix/", response_model=schemas.ExcelUploadResponse)
        async def upload_skill_matrix(
            file: UploadFile = File(...),
            db: Annotated[Session, Depends(get_db)],
            current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]
        ):
            """Upload an Excel file to update skill and role matrix. Requires Admin access."""
            if not file.filename.endswith((".xlsx", ".xls")):
                raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed.")

            try:
                contents = await file.read()
                excel_data = BytesIO(contents)

                # Call a utility function to parse and update DB
                # This function should be implemented in utils.py and handle the actual DB updates
                result_message, details = parse_excel_skill_matrix(db, excel_data)

                return {"message": result_message, "details": details}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to process Excel file: {str(e)}")

        # In utils.py
        # You need to implement this with pandas to read specific sheets and update models
        def parse_excel_skill_matrix(db: Session, excel_file: BytesIO):
            """
            Parses the uploaded Excel file and updates the database with skills,
            proficiency levels, project roles, and role-skill requirements.
            """
            # Implement detailed pandas logic here to read sheets and interact with crud functions
            # Example:
            # xls = pd.ExcelFile(excel_file)
            # skills_df = pd.read_excel(xls, sheet_name='Skills')
            # for index, row in skills_df.iterrows():
            #     crud.create_skill(db, schemas.SkillCreate(name=row['Skill Name'], description=row['Description']))
            # ... similar logic for other sheets and models
            # Return a summary of changes
            return "Excel processed successfully", {"skills_added": 5, "roles_updated": 2}
        ```

**Task 2.4: Skill Gap Analysis Endpoints**
- **Action:** Implement an API endpoint to calculate and report skill gaps for developers.
- **Instructions:**
    1.  **Endpoint:** `GET /admin/skill-gaps/`
    2.  **Logic:**
        * Fetch all users, their assigned project roles, their current skills, and the required skills for their roles.
        * Compare current skills/proficiency against required skills/proficiency for each developer.
        * Generate a report indicating the skill gaps (e.g., `developer_name`, `role`, `required_skill`, `required_proficiency`, `current_proficiency`, `gap_identified`).
        * Return the report as `schemas.SkillGapReportResponse`.
    3.  **This will likely involve complex SQLAlchemy queries with joins.**
    4.  **Ensure it requires `get_current_admin_user`.**

**Task 2.5: Learning Path & Course Management Endpoints (Assign/Bulk Assign)**
- **Action:** Implement CRUD for courses and learning paths. Add endpoints for assigning learning paths/courses to individuals and in bulk.
- **Instructions:**
    1.  **Add comprehensive CRUD endpoints for `courses`, `learning_paths`, and `learning_path_courses` to `main.py`, requiring `get_current_admin_user`.**
    2.  **Implement assignment endpoints:**
        * `POST /admin/assign-learning-path/individual` (Assign one learning path to one user)
        * `POST /admin/assign-learning-path/bulk` (Assign one learning path to multiple users, or multiple learning paths to one user, or multiple learning paths to multiple users based on criteria).
    3.  **These endpoints will primarily interact with the `user_learning_paths` table.**

**Task 2.6: Reporting Endpoints (Lagging Progress, Compliance)**
- **Action:** Implement API endpoints to generate reports on individual progress and overall compliance.
- **Instructions:**
    1.  **Endpoint:** `GET /admin/reports/lagging-progress`
        * **Logic:** Identify users whose `user_course_progress` or `user_learning_paths` status indicates they are falling behind (e.g., 'In Progress' for too long, or past a simulated due date).
        * Return `schemas.LaggingProgressReportResponse`.
    2.  **Endpoint:** `GET /admin/reports/compliance`
        * **Logic:** Calculate overall and designation-wise compliance on course completion based on `user_course_progress` and `user_learning_paths`.
        * Return `schemas.ComplianceReportResponse`.
    3.  **Ensure both require `get_current_admin_user`.**

---

### **Phase 3: Core API Endpoints (Developer Features)**

**Task 3.1: Developer-Specific Endpoints**
- **Action:** Implement API endpoints for developers to view their assigned courses, mandatory/optional courses, progress, and to register for courses.
- **Instructions:**
    1.  **Ensure all developer endpoints use `Depends(get_current_user)` for authorization (not `get_current_admin_user`).**
    2.  **Endpoint:** `GET /developer/my-courses/`
        * **Logic:** Retrieve all learning paths/courses where the current developer is registered (`user_learning_paths`).
        * Return `List[schemas.UserLearningPathResponse]` (or a simplified DTO).
    3.  **Endpoint:** `GET /developer/mandatory-learning/`
        * **Logic:** Identify learning paths/courses that are mandatory for the developer's current role based on skill gaps, but not yet registered for.
        * Return `List[schemas.LearningPathResponse]`.
    4.  **Endpoint:** `GET /developer/optional-recommendations/`
        * **Logic:** Suggest optional courses based on system recommendations (e.g., skills adjacent to their current ones, or popular courses).
        * Return `List[schemas.CourseResponse]`.
    5.  **Endpoint:** `GET /developer/popular-courses/`
        * **Logic:** Fetch courses marked as popular or based on enrollment counts by peers.
        * Return `List[schemas.CourseResponse]`.
    6.  **Endpoint:** `POST /developer/register-course/{course_id}`
        * **Logic:** Allow a developer to register for a course (updates `user_learning_paths` or `user_course_progress`).
    7.  **Endpoint:** `GET /developer/my-progress/`
        * **Logic:** Retrieve individual and combined progress on all courses (`user_course_progress`).
        * Return `List[schemas.UserCourseProgressResponse]`.
    8.  **Endpoint:** `PUT /developer/update-course-progress/{progress_id}`
        * **Logic:** Allow developer to update their progress (e.g., mark as completed, update percentage) – *Note: In a real LMS, this is usually driven by external learning platforms or course completion logic, but for internal tracking, this simulates it.*

---

### **Phase 4: Advanced Features & Integration**

**Task 4.1: Unutilized Skills Reporting**
- **Action:** Implement an API endpoint to identify and report skills available within associates that are not being utilized in their current roles.
- **Instructions:**
    1.  **Endpoint:** `GET /admin/reports/unutilized-skills`
    2.  **Logic:**
        * Compare `user_skills` with `role_skill_requirements` for each user.
        * Identify skills a user possesses (`user_skills`) that are not part of their `current_project_role`'s `role_skill_requirements` or are above the required proficiency for their current role.
        * Return a structured report.
    3.  **Requires `get_current_admin_user`.**

**Task 4.2: Role-Skill Swap Suggestions**
- **Action:** Implement an API endpoint to suggest swapping role-skill combinations between people to reduce overall skill gaps and enhance fitment.
- **Instructions:**
    1.  **Endpoint:** `GET /admin/suggestions/role-skill-swaps`
    2.  **Logic:**
        * This is a complex optimization problem. The core logic would involve:
            * Calculating skill gaps for all developers.
            * Identifying developers with significant gaps in their current role.
            * Identifying developers with underutilized skills.
            * Proposing hypothetical swaps of project roles between two or more developers.
            * Recalculating the combined skill gaps after the hypothetical swap.
            * Suggesting swaps that lead to a net reduction in overall skill gaps or better utilization of specific skills.
        * **Initial approach could be rule-based (e.g., "if X has skill A and Y needs skill A, and X needs skill B and Y has skill B, suggest swap"). Future iterations could use more advanced algorithms.**
        * Return `List[schemas.RoleSkillSwapSuggestion]`.
    3.  **Requires `get_current_admin_user`.**

**Task 4.3: Chatbot API Integration (Backend Processing)**
- **Action:** Implement API endpoints that act as intermediaries for the frontend chatbot requests. These endpoints will query the database based on prompts and return structured data.
- **Instructions:**
    1.  **Endpoint:** `POST /chatbot/query/admin`
        * **Accepts:** `{"prompt": "string"}` (Admin's query, e.g., "Provide me the course wise completion % for employee ID 123456")
        * **Logic:**
            * Parse the prompt (simple keyword matching initially, or use a basic NLP library if Copilot can suggest lightweight ones for Python, like `spaCy` or `NLTK`, but keep it simple for now).
            * Based on keywords (e.g., "completion %", "employee ID"), formulate a database query using SQLAlchemy.
            * Fetch relevant data (e.g., from `user_course_progress`, `users`).
            * Format the data into a human-readable response string or a small JSON object.
            * **Security:** Ensure the query is validated and does not allow SQL injection.
        * **Return:** `{"response": "string", "data": optional_json_object}`
        * **Requires `get_current_admin_user`.**
    2.  **Endpoint:** `POST /chatbot/query/developer`
        * **Accepts:** `{"prompt": "string"}` (Developer's query, e.g., "Provide me the course wise completion % for me")
        * **Logic:** Similar to admin chatbot, but **strictly filter data to the current authenticated developer's ID**.
        * **Return:** `{"response": "string", "data": optional_json_object}`
        * **Requires `get_current_user`.**
        * **Crucial:** Emphasize that this endpoint *must not* expose data of other users.

---

### **General Instructions for Copilot Agent:**

1.  **Modular Design:** Organize code into logical modules (e.g., `main.py` for FastAPI app/routes, `models.py` for SQLAlchemy models, `schemas.py` for Pydantic models, `crud.py` for database operations, `utils.py` for helper functions like Excel parsing).
2.  **Dependencies:** Use FastAPI's dependency injection extensively, especially for `Depends(get_db)` and authentication (`Depends(get_current_user)`, `Depends(get_current_admin_user)`).
3.  **Error Handling:** Use FastAPI's `HTTPException` for API errors (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error).
4.  **Logging:** Implement basic logging for API requests, errors, and significant events.
5.  **Security:**
    * **Password Hashing:** Ensure `bcrypt` is used for hashing passwords.
    * **JWT:** Correctly implement JWT creation and validation.
    * **Authorization:** Strictly enforce role-based access control using dependencies (Admin vs. Developer).
    * **Input Validation:** Use Pydantic models for request body validation.
6.  **Database Interactions:** All database operations should go through SQLAlchemy ORM, preferably via functions in `crud.py`. Avoid raw SQL queries directly in endpoints.
7.  **Docstrings and Type Hints:** Use clear docstrings for functions and classes, and Python type hints for better code readability and maintainability.
8.  **Testing (Conceptual):** While not implementing tests directly, hint at the need for unit and integration tests for key functions (e.g., `crud` operations, skill gap calculations).
9.  **Database Migrations (Future Consideration):** Mention that for production, a tool like Alembic would be used for database migrations.

**After generating the code for each task, please provide instructions on how to continue to the next task or how to run the application (e.g., `uvicorn main:app --reload`).**

Let's begin by following these instructions step by step.
