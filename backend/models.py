from sqlmodel import SQLModel, Field, Relationship, create_engine
from typing import Optional, List
from enum import Enum
import hashlib
import secrets

from config import DATABASE_URL


# ============== PASSWORD UTILITIES ==============

def generate_salt() -> str:
    return secrets.token_hex(32)


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100000
    ).hex()


def verify_password(password: str, salt: str, hashed: str) -> bool:
    return hash_password(password, salt) == hashed


# ============== ENUMS ==============

class Privilege(str, Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


# ============== MODELS ==============

class Group(SQLModel, table=True):
    IDg: Optional[int] = Field(default=None, primary_key=True)
    Name: str

    users: List["User"] = Relationship(back_populates="group")
    events: List["Event"] = Relationship(back_populates="group")


class User(SQLModel, table=True):
    IDu: Optional[int] = Field(default=None, primary_key=True)
    IDg: Optional[int] = Field(default=None, foreign_key="group.IDg")
    privilege: Privilege = Field(default=Privilege.user)
    Password: str
    Salt: str

    group: Optional[Group] = Relationship(back_populates="users")
    sessions: List["Session"] = Relationship(back_populates="user")


class Event(SQLModel, table=True):
    IDe: Optional[int] = Field(default=None, primary_key=True)
    IDg: Optional[int] = Field(default=None, foreign_key="group.IDg")
    IsPublic: bool = Field(default=True)
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None
    Address: Optional[str] = None
    Description: Optional[str] = None
    Name: str
    Size: Optional[int] = None

    group: Optional[Group] = Relationship(back_populates="events")


class Session(SQLModel, table=True):
    Cookie: str = Field(primary_key=True)
    IDu: Optional[int] = Field(default=None, foreign_key="user.IDu")
    IsLoggedIn: bool = Field(default=False)

    user: Optional[User] = Relationship(back_populates="sessions")


# ============== DATABASE SETUP ==============

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()