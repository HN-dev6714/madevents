import duckdb
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Response, Cookie
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# --- Database Setup ---
DB_PATH = "app.duckdb"

def get_db():
    conn = duckdb.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = duckdb.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "Group" (
            IDg INTEGER PRIMARY KEY,
            Name VARCHAR NOT NULL UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "User" (
            IDu INTEGER PRIMARY KEY,
            Privilege VARCHAR DEFAULT 'user',
            Username VARCHAR NOT NULL UNIQUE,
            PasswordHash VARCHAR NOT NULL,
            Salt VARCHAR NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Event (
            IDe INTEGER PRIMARY KEY,
            IsPublic BOOLEAN DEFAULT FALSE,
            Latitude VARCHAR NOT NULL,
            Longitude VARCHAR NOT NULL,
            Address VARCHAR NOT NULL,
            Description TEXT,
            Name VARCHAR NOT NULL,
            Size INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Session (
            Cookie VARCHAR PRIMARY KEY,
            IDu INTEGER REFERENCES "User"(IDu),
            IsLoggedIn BOOLEAN DEFAULT FALSE,
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS UserGroups (
            IDug INTEGER PRIMARY KEY,
            IDu INTEGER REFERENCES "User"(IDu),
            IDg INTEGER REFERENCES "Group"(IDg)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS GroupEvents (
            IDge INTEGER PRIMARY KEY,
            IDg INTEGER REFERENCES "Group"(IDg),
            IDe INTEGER REFERENCES "Event"(IDe)
        )
    """)
    # Create sequences for auto-increment
    conn.execute("CREATE SEQUENCE IF NOT EXISTS user_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS group_seq START 2")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS event_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS user_group_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS group_event_seq START 1")

    # Insert default group 'public' with ID 1.
    # 'ON CONFLICT DO NOTHING' ensures this doesn't crash if the group already exists.
    conn.execute(
        """
        INSERT INTO "Group" (IDg, Name) 
        VALUES (1, 'public') 
        ON CONFLICT (IDg) DO NOTHING
        """
    )

    conn.close()

class GroupCreateResponse(BaseModel):
    msg: str

class GetGroupResponse(BaseModel):
    group_names: list[str]

class UserCreateRequest(BaseModel):
    Username: str
    Password: str

class UserCreateResponse(BaseModel):
    msg: str

class EventCreateRequest(BaseModel):
    Group: str
    IsPublic: bool
    Longitude: str
    Latitude: str
    Address: str
    Description: Optional[str] = None
    Name: str
    Size: Optional[int] = 0

class EventCreateResponse(BaseModel):
    msg: str

class LoginRequest(BaseModel):
    Username: str
    Password: str

class LoginResponse(BaseModel):
    msg: str

class LogoutResponse(BaseModel):
    msg: str

class GetEventResponse(BaseModel):
    Longitude: str
    Latitude: str
    Address: str
    Description: Optional[str] = None
    Name: str
    Size: int


# --- Auth Helpers ---
def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, salt: str, hash: str) -> bool:
    return hash_password(password, salt) == hash

def create_session(conn, user_id: int, is_login: bool) -> str:
    cookie = secrets.token_urlsafe(32)
    conn.execute(
        "INSERT INTO Session (Cookie, IDu, IsLoggedIn) VALUES (?, ?, ?)",
        [cookie, user_id, is_login]
    )
    return cookie

def get_current_user(session_cookie: Optional[str] = Cookie(None), conn=Depends(get_db)):
    if not session_cookie:
        raise HTTPException(401, "Not authenticated")
    result = conn.execute(
        "SELECT IDu FROM Session WHERE Cookie = ? AND IsLoggedIn = TRUE",
        [session_cookie]
    ).fetchone()
    if not result:
        raise HTTPException(401, "Invalid or expired session")
    return result[0]

# --- App Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ GROUP ENDPOINTS ------------------

@app.post("/groups", response_model=GroupCreateResponse)
def create_group(group: str, conn=Depends(get_db), user_id=Depends(get_current_user)):
    priv = conn.execute(
        """
        SELECT Privilege FROM "User" WHERE IDu = ?
        """,
        [user_id]
    ).fetchone()[0]

    if priv != "admin":
        raise HTTPException(401, "Not admin")

    conn.execute(
        """
        INSERT INTO "Group" (IDg, Name)
        VALUES (nextval('group_seq'), ?)
        """, [group]
    )
    return {"msg": "success"}


@app.get("/groups/{user_name}", response_model=GetGroupResponse)
def get_group(user_name: str, conn=Depends(get_db)):
    # Get user ID by user name
    row = conn.execute('SELECT IDu FROM "User" WHERE Username = ?', [user_name]).fetchone()
    if not row:
        raise HTTPException(404, "User not found")
    user_id = row[0]

    # Get a list of group IDs that the user belongs to
    rows = conn.execute('SELECT IDg FROM "UserGroups" WHERE IDu = ?', [user_id]).fetchall()
    if not rows:
        raise HTTPException(500, "Internal Server Error")
    group_ids = [gid[0] for gid in rows]

    # get a list of group names based on the group IDs
    rows = conn.execute('SELECT Name FROM "Group" WHERE IDg IN (SELECT unnest(?))', [group_ids]).fetchall()
    if not rows:
        raise HTTPException(500, "Internal Server Error")
    group_names = [group_name[0] for group_name in rows]
    return {"group_names": group_names}


# ------------------ USER ENDPOINTS ------------------

@app.post("/users", response_model=UserCreateResponse)
def create_user(user: UserCreateRequest, conn=Depends(get_db)):
    # Validate username
    if not user.Username or user.Username.strip() == "":
        raise HTTPException(400, "Username is required")

    # Check uniqueness
    existing = conn.execute(
        'SELECT IDu FROM "User" WHERE Username = ?',
        [user.Username]
    ).fetchone()
    if existing:
        raise HTTPException(400, "Username already taken")

    # Hash password
    salt = secrets.token_hex(16)
    hashed = hash_password(user.Password, salt)

    # Add user to database
    # To User table
    conn.begin()

    user_id = conn.execute(
        """
        INSERT INTO "User" (IDu, Privilege, PasswordHash, Salt, Username) 
        VALUES (nextval('user_seq'), 'user', ?, ?, ?)
        RETURNING IDu
        """,
        [hashed, salt, user.Username]
    ).fetchone()[0]

    # To UserGroup table
    conn.execute(
        """
        INSERT INTO "UserGroups" (IDug, IDu, IDg)
        VALUES (nextval('user_group_seq'), ?, 1)
        """,
        [user_id]
    )

    conn.commit()

    return {"msg": "success"}

# ------------------ AUTH ENDPOINTS ------------------

@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, response: Response, conn=Depends(get_db)):
    if not req.Username or req.Username.strip() == "":
        raise HTTPException(400, "Provide Username to login")

    row = conn.execute(
        'SELECT IDu, PasswordHash, Salt FROM "User" WHERE Username = ?',
        [req.Username]
    ).fetchone()

    if not row or not verify_password(req.Password, row[2], row[1]):
        raise HTTPException(401, "Invalid credentials")

    user_id = row[0]
    cookie = create_session(conn, user_id, True)
    response.set_cookie("session_cookie", cookie, httponly=True, max_age=604800)
    return {"msg": "success"}


@app.post("/logout", response_model=LogoutResponse)
def logout(response: Response, session_cookie: Optional[str] = Cookie(None), conn=Depends(get_db)):
    if session_cookie:
        conn.execute("UPDATE Session SET IsLoggedIn = FALSE WHERE Cookie = ?", [session_cookie])
        response.delete_cookie("session_cookie")
    
    return {"msg": "success"}


# ------------------ EVENT ENDPOINTS ------------------

@app.post("/events", response_model=EventCreateResponse)
def create_event(event: EventCreateRequest, conn=Depends(get_db), user_id=Depends(get_current_user)):
    priv = conn.execute(
        """
        SELECT Privilege FROM "User" WHERE IDu = ?
        """,
        [user_id]
    ).fetchone()[0]

    if priv != "admin":
        raise HTTPException(401, "Not admin")

    conn.begin()

    event_id = conn.execute(
        """
        INSERT INTO Event (IDe, IsPublic, Longitude, Latitude, Address, Description, Name, Size)
        VALUES (nextval('event_seq'), ?, ?, ?, ?, ?, ?, ?)
        RETURNING IDe
        """, [
        event.IsPublic, event.Longitude, event.Latitude, event.Address,
        event.Description, event.Name, event.Size
    ]).fetchone()[0]

    group_id = conn.execute(
        """
        SELECT IDg FROM "Group" WHERE Name = ?
        """, [event.Group]
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO GroupEvents (IDge, IDg, IDe)
        VALUES (nextval('group_event_seq'), ?, ?)
        """, [group_id, event_id]
    )

    conn.commit()

    return {"msg": "success"}


@app.get("/events", response_model=list[GetEventResponse])
def list_events(conn=Depends(get_db), session_cookie: Optional[str] = Cookie(None)):
    # Try retrieving user; ignore if not logged in
    try:
        user_id = get_current_user(session_cookie=session_cookie, conn=conn)
    except:
        user_id = None

    if user_id:
        priv = conn.execute(
            """
            SELECT Privilege FROM "User" WHERE IDu = ?
            """,
            [user_id]
        ).fetchone()[0]

        if priv == 'user':
            rows = conn.execute("""
                SELECT * FROM Event WHERE IsPublic = TRUE

                UNION

                SELECT E.*
                FROM Event E
                JOIN GroupEvents GE ON E.IDe = GE.IDe
                JOIN UserGroups UG ON GE.IDg = UG.IDg
                WHERE UG.IDu = ?
                """, [user_id]).fetchall()

        if priv == 'admin':
            rows = conn.execute(
                """
                SELECT * FROM Event
                """
            ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM Event WHERE IsPublic = TRUE").fetchall()

    return [
        {"Latitude": r[2], "Longitude": r[3], "Address": r[4], "Description": r[5],
         "Name": r[6], "Size": r[7]}
        for r in rows
    ]


# @app.get("/events/{id}", response_model=EventResponse)
# def get_event(id: int, conn=Depends(get_db)):
#     row = conn.execute("SELECT * FROM Event WHERE IDe = ?", [id]).fetchone()
#     if not row:
#         raise HTTPException(404, "Event not found")
#     if not row[2]:
#         raise HTTPException(403, "Private event")
# 
#     return {"IDe": row[0], "IDg": row[1], "IsPublic": row[2], "Position": row[3],
#             "Address": row[4], "Description": row[5], "Name": row[6], "Size": row[7]}
# 
# 
# @app.delete("/events/{id}")
# def delete_event(id: int, conn=Depends(get_db), user_id=Depends(get_current_user)):
#     conn.execute("DELETE FROM Event WHERE IDe = ?", [id])
#     return {"message": "Event deleted"}
# 
# 
# ------------------ RUN ------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
