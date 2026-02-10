
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    role: str = "viewer" # admin, viewer
    full_name: str | None = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    password: str | None = None
