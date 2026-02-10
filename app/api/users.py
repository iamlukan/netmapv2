
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.repository.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.deps import get_current_admin_user
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    db_user = UserRepository.get_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    # Default to viewer if invalid role passed
    role = user.role if user.role in ["admin", "editor", "viewer"] else "viewer" # Actually handled by pydantic ideally but safe here
    
    new_user = User(
        username=user.username, 
        hashed_password=hashed_password, 
        role=role, 
        full_name=user.full_name
    )
    UserRepository.create_user(db, new_user)
    return new_user

@router.get("/users", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    return UserRepository.get_all(db)

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # CRITICAL: Prevent modifying the main 'admin' user's role or password via API if it is THE admin
    if user.username == "admin":
        if user_update.role and user_update.role != "admin":
             raise HTTPException(status_code=400, detail="Cannot downgrade the super-admin user.")
    
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
         user.role = user_update.role
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # CRITICAL PROTECTION
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete the super-admin user.")
        
    db.delete(user)
    db.commit()
    return {"status": "deleted", "username": user.username}
