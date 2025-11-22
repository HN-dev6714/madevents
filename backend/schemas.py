from pydantic import BaseModel
from typing import Optional
from models import Privilege


# ============== USER SCHEMAS ==============

class UserCreate(BaseModel):
    Password: str
    IDg: Optional[int] = None
    privilege: Privilege = Privilege.user


class UserUpdate(BaseModel):
    IDg: Optional[int] = None
    privilege: Optional[Privilege] = None


class UserResponse(BaseModel):
    IDu: int
    IDg: Optional[int]
    privilege: Privilege


# ============== AUTH SCHEMAS ==============

class UserLogin(BaseModel):
    IDu: int
    Password: str


class LoginResponse(BaseModel):
    cookie: str
    user_id: int


# ============== GROUP SCHEMAS ==============

class GroupCreate(BaseModel):
    Name: str


class GroupResponse(BaseModel):
    IDg: int
    Name: str


# ============== EVENT SCHEMAS ==============

class EventCreate(BaseModel):
    IDg: Optional[int] = None
    IsPublic: bool = True
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None
    Address: Optional[str] = None
    Description: Optional[str] = None
    Name: str
    Size: Optional[int] = None


class EventUpdate(BaseModel):
    IDg: Optional[int] = None
    IsPublic: Optional[bool] = None
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None
    Address: Optional[str] = None
    Description: Optional[str] = None
    Name: Optional[str] = None
    Size: Optional[int] = None


class EventResponse(BaseModel):
    IDe: int
    IDg: Optional[int]
    IsPublic: bool
    Latitude: Optional[float]
    Longitude: Optional[float]
    Address: Optional[str]
    Description: Optional[str]
    Name: str
    Size: Optional[int]