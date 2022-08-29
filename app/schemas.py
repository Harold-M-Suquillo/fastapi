from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.config import settings
from pydantic.types import conint

# posts
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    post_id: int
    user_id: int
    created_at: datetime

# users
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class UserDataResponse(BaseModel):
    id: int
    created_at: datetime
    email: EmailStr

# authentication
class userLogin(BaseModel):
    email: EmailStr
    password: str

# The response format for login
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class CurrentUser(BaseModel):
    id: int
    email: EmailStr
    age: int

# ---------- Vote ----------
class Vote(BaseModel):
    post_id: int
    dir: conint(le=1, ge=0)
