from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from app.models.user import User
from app.repository.user_repository import UserRepository
from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Tables initialized in main.py

router = APIRouter()

@router.post("/auth/login")
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserRepository.get_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user.role, 
        "full_name": user.full_name,
        "force_password_change": user.force_password_change
    }

from app.schemas.user import UserCreate, UserResponse
from app.core.deps import get_current_admin_user
from app.core.security import get_password_hash

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    db_user = UserRepository.get_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password, role=user.role, full_name=user.full_name)
    UserRepository.create_user(db, new_user)
    return new_user

@router.get("/users", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    return UserRepository.get_all(db)
