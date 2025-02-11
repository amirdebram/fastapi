from pydantic import BaseModel, EmailStr
from typing import Union

class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str

class User(UserBase):
    id: int
    hashed_password: str

class UserPublic(UserBase):
    id: int
    is_admin: bool
    is_active: bool

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    username: Union[str, None] = None
    email: Union[EmailStr, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    password: Union[str, None] = None
    is_active: Union[bool, None] = None
    