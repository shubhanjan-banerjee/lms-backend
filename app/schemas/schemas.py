from pydantic import BaseModel, EmailStr
from typing import List, Optional, TYPE_CHECKING, ForwardRef
from datetime import datetime

UserLearningPathResponse = ForwardRef('UserLearningPathResponse')
UserCourseProgressResponse = ForwardRef('UserCourseProgressResponse')

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    sso_id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    current_project_role: Optional[dict] = None
    date_joined: datetime
    last_login: Optional[datetime] = None
    user_skills: List[dict] = []
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    sso_id: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str

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

class SkillResponse(SkillBase):
    id: int
    class Config:
        from_attributes = True

class ProficiencyLevelBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProficiencyLevelCreate(ProficiencyLevelBase):
    pass

class ProficiencyLevelResponse(ProficiencyLevelBase):
    id: int
    class Config:
        from_attributes = True

class ProjectRoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectRoleCreate(ProjectRoleBase):
    pass

class ProjectRoleResponse(ProjectRoleBase):
    id: int
    class Config:
        from_attributes = True

class UserSkillBase(BaseModel):
    user_id: int
    skill_id: int
    proficiency_level_id: int

class UserSkillCreate(UserSkillBase):
    pass

class UserSkillResponse(UserSkillBase):
    id: int
    class Config:
        from_attributes = True

class RoleSkillRequirementBase(BaseModel):
    project_role_id: int
    skill_id: int
    min_proficiency_level_id: int
    is_mandatory: bool = True

class RoleSkillRequirementCreate(RoleSkillRequirementBase):
    pass

class RoleSkillRequirementResponse(RoleSkillRequirementBase):
    id: int
    class Config:
        from_attributes = True

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
        from_attributes = True

class ProficiencyLevelResponse(ProficiencyLevelBase):
    id: int
    class Config:
        from_attributes = True

class ProjectRoleResponse(ProjectRoleBase):
    id: int
    class Config:
        from_attributes = True

class UserSkillResponse(UserSkillBase):
    id: int
    class Config:
        from_attributes = True

class RoleSkillRequirementResponse(RoleSkillRequirementBase):
    id: int
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    sso_id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    current_project_role: Optional[ProjectRoleResponse] = None
    date_joined: datetime
    last_login: Optional[datetime] = None
    user_skills: List[UserSkillResponse] = []
    user_learning_paths: List[UserLearningPathResponse] = []
    user_course_progress: List[UserCourseProgressResponse] = []
    class Config:
        from_attributes = True

class CourseResponse(CourseBase):
    id: int
    skill: Optional[SkillResponse] = None
    recommended_proficiency_level: Optional[ProficiencyLevelResponse] = None
    class Config:
        from_attributes = True

class LearningPathCourseResponse(LearningPathCourseBase):
    id: int
    course: CourseResponse
    class Config:
        from_attributes = True

class LearningPathResponse(LearningPathBase):
    id: int
    courses: List[LearningPathCourseResponse] = []
    class Config:
        from_attributes = True

class UserLearningPathResponse(UserLearningPathBase):
    id: int
    learning_path: LearningPathResponse
    class Config:
        from_attributes = True

class UserCourseProgressResponse(UserCourseProgressBase):
    id: int
    course: CourseResponse
    class Config:
        from_attributes = True

class AuditLogResponse(AuditLogBase):
    id: int
    class Config:
        from_attributes = True

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
    username: str
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

class UserSkillDisplay(BaseModel):
    skill_id: int
    skill_name: str
    proficiency_level_id: int
    proficiency_level_name: str
    id: int

class UserResponse(BaseModel):
    id: int
    sso_id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    current_project_role: Optional[ProjectRoleResponse] = None
    date_joined: datetime
    last_login: Optional[datetime] = None
    user_skills: List[UserSkillDisplay] = []
    user_learning_paths: List['UserLearningPathResponse'] = []
    user_course_progress: List['UserCourseProgressResponse'] = []
    class Config:
        from_attributes = True

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    UserLearningPathResponse = 'UserLearningPathResponse'
    UserCourseProgressResponse = 'UserCourseProgressResponse'
