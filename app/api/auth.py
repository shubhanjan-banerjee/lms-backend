from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Annotated, Optional
import logging

import app.models.models as models
import app.schemas.schemas as schemas
import app.crud.crud as crud
from app.core.database import get_db
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from jose import JWTError, jwt

router = APIRouter()
logger = logging.getLogger("lms_backend.api.auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_sso_id(db, sso_id=username)
    if not user or not crud.verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, role: Optional[str] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    if role:
        to_encode["role"] = role
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]
):
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
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Admin access required."
        )
    return current_user

@router.post("/token", response_model=schemas.Token)
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
        data={"sub": user.sso_id}, expires_delta=access_token_expires, role=user.role
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    # Remove password from the dict before passing to UserResponse
    user_dict = current_user.__dict__.copy()
    user_dict.pop("hashed_password", None)
    # Handle relationships for user_skills and current_project_role
    user_dict["user_skills"] = [schemas.UserSkillResponse.model_validate(us, from_attributes=True) for us in getattr(current_user, "user_skills", [])]
    if getattr(current_user, "project_role", None):
        user_dict["current_project_role"] = schemas.ProjectRoleResponse.model_validate(current_user.project_role, from_attributes=True)
    else:
        user_dict["current_project_role"] = None
    return schemas.UserResponse(**user_dict)

@router.get("/admin/me/", response_model=schemas.UserResponse)
async def read_admin_me(current_admin_user: Annotated[models.User, Depends(get_current_admin_user)]):
    return current_admin_user

@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
):
    logger.debug("/refresh endpoint accessed.")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sso_id: str = payload.get("sub")
        if sso_id is None:
            logger.warning("No subject in token during refresh.")
            raise credentials_exception
        user = crud.get_user_by_sso_id(db, sso_id=sso_id)
        if user is None:
            logger.warning("User not found during refresh.")
            raise credentials_exception
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_token = create_access_token({"sub": user.sso_id}, expires_delta=access_token_expires, role=user.role)
        logger.info(f"Refreshed token for user: {user.sso_id}")
        return {"access_token": new_token, "token_type": "bearer"}
    except JWTError as e:
        logger.error(f"JWT error during refresh: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise credentials_exception

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing_user = crud.get_user_by_sso_id(db, sso_id=user.sso_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="SSO ID already registered")
    created_user = crud.create_user(db=db, user=user)
    # Prepare response (exclude password)
    user_dict = created_user.__dict__.copy()
    user_dict.pop("hashed_password", None)
    user_dict["user_skills"] = []
    user_dict["current_project_role"] = None
    return schemas.UserResponse(**user_dict)
