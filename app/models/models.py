from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import logging

logger = logging.getLogger("lms_backend.models")

class User(Base):
    __tablename__ = "users"
    # logger.debug("Defining User model.")
    id = Column(Integer, primary_key=True, index=True)
    sso_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="Developer", nullable=False)
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
    # logger.debug("Defining Skill model.")
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    user_skills = relationship("UserSkill", back_populates="skill")
    role_skill_requirements = relationship("RoleSkillRequirement", back_populates="skill")
    courses = relationship("Course", back_populates="skill")

class ProficiencyLevel(Base):
    __tablename__ = "proficiency_levels"
    # logger.debug("Defining ProficiencyLevel model.")
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

class ProjectRole(Base):
    __tablename__ = "project_roles"
    # logger.debug("Defining ProjectRole model.")
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", back_populates="project_role")
    role_skill_requirements = relationship("RoleSkillRequirement", back_populates="project_role")

class UserSkill(Base):
    __tablename__ = "user_skills"
    # logger.debug("Defining UserSkill model.")
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency_level_id = Column(Integer, ForeignKey("proficiency_levels.id"), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")
    proficiency_level = relationship("ProficiencyLevel")

class RoleSkillRequirement(Base):
    __tablename__ = "role_skill_requirements"
    # logger.debug("Defining RoleSkillRequirement model.")
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
    # logger.debug("Defining Course model.")
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    provider = Column(String(255), nullable=True)
    duration_hours = Column(Integer, nullable=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    recommended_proficiency_level_id = Column(Integer, ForeignKey("proficiency_levels.id"), nullable=True)
    image_url = Column(String(255), nullable=True)

    skill = relationship("Skill", back_populates="courses")
    recommended_proficiency_level = relationship("ProficiencyLevel")
    learning_path_courses = relationship("LearningPathCourse", back_populates="course")
    user_course_progress = relationship("UserCourseProgress", back_populates="course")

class LearningPath(Base):
    __tablename__ = "learning_paths"
    # logger.debug("Defining LearningPath model.")
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    learning_path_courses = relationship("LearningPathCourse", back_populates="learning_path")
    user_learning_paths = relationship("UserLearningPath", back_populates="learning_path")

class LearningPathCourse(Base):
    __tablename__ = "learning_path_courses"
    # logger.debug("Defining LearningPathCourse model.")
    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    sequence_order = Column(Integer, nullable=False)

    learning_path = relationship("LearningPath", back_populates="learning_path_courses")
    course = relationship("Course", back_populates="learning_path_courses")

class UserLearningPath(Base):
    __tablename__ = "user_learning_paths"
    # logger.debug("Defining UserLearningPath model.")
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    assigned_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="Assigned", nullable=False)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    is_mandatory_by_system = Column(Boolean, default=False, nullable=False)
    is_registered_by_developer = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="user_learning_paths")
    learning_path = relationship("LearningPath", back_populates="user_learning_paths")

class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    # logger.debug("Defining UserCourseProgress model.")
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(String(50), default="Not Started", nullable=False)
    progress_percentage = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completion_date = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="user_course_progress")
    course = relationship("Course", back_populates="user_course_progress")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    # logger.debug("Defining AuditLog model.")
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    admin_user = relationship("User", back_populates="audit_logs")
