import duckdb
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Response, Cookie
from pydantic import BaseModel
from contextlib import asynccontextmanager

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
            IsPublic BOOLEAN DEFAULT TRUE,
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
    conn.execute("CREATE SEQUENCE IF NOT EXISTS group_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS event_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS user_group_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS group_event_seq START 1")
    conn.close()

class GroupCreateRequest(BaseModel):
    Name: str

class GroupCreateResponse(BaseModel):
    msg: str

class GetGroupRequest(BaseModel):
    Name: str

class GetGroupResponse(BaseModel):
    group_names: list[str]

class UserCreate(BaseModel):
    Privilege: str = "user"
    Username: str
    Password: str

class UserResponse(BaseModel):
    msg: str

class EventCreate(BaseModel):
    IsPublic: bool
    Longitude: str
    Latitude: str
    Address: str
    Description: Optional[str] = None
    Name: str
    Size: Optional[int] = 0

class EventResponse(BaseModel):
    msg: str

class LoginRequest(BaseModel):
    Username: str
    Password: str

class LoginResponse(BaseModel):
    msg: str

class UserGroupCreate(BaseModel):
    IDu: int
    IDg: int

class UserGroupResponse(BaseModel):
    msg: str

class GroupEventCreate(BaseModel):
    IDg: int
    IDe: int

class GroupEventResponse(BaseModel):
    msg: str

# --- Auth Helpers ---
def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, salt: str, hash: str) -> bool:
    return hash_password(password, salt) == hash

def create_session(conn, user_id: int) -> str:
    cookie = secrets.token_urlsafe(32)
    conn.execute(
        "INSERT INTO Session (Cookie, IDu, IsLoggedIn) VALUES (?, ?, FALSE)",
        [cookie, user_id]
    )
    return cookie

async def get_current_user(session_cookie: Optional[str] = Cookie(None), conn=Depends(get_db)):
    if not session_cookie:
        raise HTTPException(401, "Not authenticated")
    result = conn.execute(
        "SELECT IDu FROM Session WHERE Cookie = ? AND IsLoggedIn = TRUE AND ExpiresAt > ?",
        [session_cookie, datetime.now()]
    ).fetchone()
    if not result:
        raise HTTPException(401, "Invalid or expired session")
    return result[0]

# --- App Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Event Management API", lifespan=lifespan)

# ------------------ GROUP ENDPOINTS ------------------

@app.post("/groups", response_model=GroupCreateResponse)
def create_group(group: GroupCreateRequest, conn=Depends(get_db)):
    conn.execute('INSERT INTO "Group" (Name) VALUES (?)', [group.Name])
    id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {"msg": "success"}


# @app.get("/groups", response_model=list[GroupResponse])
# def list_groups(conn=Depends(get_db)):
#     rows = conn.execute('SELECT IDg, Name FROM "Group"').fetchall()
#     return [{"IDg": r[0], "Name": r[1]} for r in rows]


@app.get("/groups/{user_name}", response_model=GetGroupResponse)
def get_group(user_name: GetGroupRequest, conn=Depends(get_db)):
    # Get user ID by user name
    row = conn.execute('SELECT IDu FROM "User" WHERE Username = ?', [user_name.Name]).fetchone()
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

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, conn=Depends(get_db)):
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

    # Get ID and Insert in one atomic statement
    # Note: We use nextval inside the insert and RETURN the IDu
    row = conn.execute(
        """
        INSERT INTO "User" (IDu, IDg, Privilege, PasswordHash, Salt, Username) 
        VALUES (nextval('user_seq'), ?, ?, ?, ?, ?)
        RETURNING IDu
        """,
        [user.IDg, user.Privilege, hashed, salt, user.Username]
    ).fetchone()
    
    id = row[0]
    return {"IDu": id, "IDg": user.IDg, "Privilege": user.Privilege, "Username": user.Username}

@app.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, conn=Depends(get_db), _=Depends(get_current_user)):
    row = conn.execute(
        'SELECT IDu, IDg, Privilege, Username FROM "User" WHERE IDu = ?',
        [id]
    ).fetchone()

    if not row:
        raise HTTPException(404, "User not found")

    return {"IDu": row[0], "IDg": row[1], "Privilege": row[2], "Username": row[3]}

# ------------------ USERGROUPS ENDPOINTS ------------------

@app.post("/user-groups", response_model=UserGroupResponse)
def add_user_to_group(ug: UserGroupCreate, conn=Depends(get_db), user_id=Depends(get_current_user)):
    # Check if the user trying to add is an admin (optional, for basic implementation we just check for login)
    # A more robust system would check if 'user_id' is an admin of 'ug.IDg'

    # Check for existing record to prevent duplicates
    existing = conn.execute(
        "SELECT IDug FROM UserGroups WHERE IDu = ? AND IDg = ?",
        [ug.IDu, ug.IDg]
    ).fetchone()

    if existing:
        raise HTTPException(400, "User is already in this group")
    
    # Check if user and group exist before inserting
    user_exists = conn.execute('SELECT 1 FROM "User" WHERE IDu = ?', [ug.IDu]).fetchone()
    group_exists = conn.execute('SELECT 1 FROM "Group" WHERE IDg = ?', [ug.IDg]).fetchone()
    
    if not user_exists or not group_exists:
        raise HTTPException(404, "User or Group not found")

    conn.execute(
        "INSERT INTO UserGroups (IDu, IDg) VALUES (?, ?)",
        [ug.IDu, ug.IDg]
    )
    
    id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {"IDug": id, "IDu": ug.IDu, "IDg": ug.IDg}


@app.get("/user-groups/{user_id}", response_model=list[GroupResponse])
def get_groups_for_user(user_id: int, conn=Depends(get_db), _=Depends(get_current_user)):
    # Get all groups a specific user belongs to
    rows = conn.execute("""
        SELECT 
            G.IDg, G.Name 
        FROM UserGroups AS UG
        JOIN "Group" AS G ON UG.IDg = G.IDg
        WHERE UG.IDu = ?
    """, [user_id]).fetchall()

    return [{"IDg": r[0], "Name": r[1]} for r in rows]

# TODO: Do we need an endpoint for getting users for a specific group?

# ------------------ GROUPEVENTS ENDPOINTS ------------------

@app.post("/group-events", response_model=GroupEventResponse)
def link_event_to_group(ge: GroupEventCreate, conn=Depends(get_db), user_id=Depends(get_current_user)):
    # Authenticated check is important for managing which events belong to which groups

    # Check for existing record
    existing = conn.execute(
        "SELECT IDge FROM GroupEvents WHERE IDg = ? AND IDe = ?",
        [ge.IDg, ge.IDe]
    ).fetchone()
    
    if existing:
        raise HTTPException(400, "Event is already linked to this group")

    # Check if group and event exist before inserting
    group_exists = conn.execute('SELECT 1 FROM "Group" WHERE IDg = ?', [ge.IDg]).fetchone()
    event_exists = conn.execute('SELECT 1 FROM Event WHERE IDe = ?', [ge.IDe]).fetchone()

    if not group_exists or not event_exists:
        raise HTTPException(404, "Group or Event not found")

    conn.execute(
        "INSERT INTO GroupEvents (IDg, IDe) VALUES (?, ?)",
        [ge.IDg, ge.IDe]
    )
    
    id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {"IDge": id, "IDg": ge.IDg, "IDe": ge.IDe}


@app.get("/group-events/{group_id}", response_model=list[EventResponse])
def get_events_for_group(group_id: int, conn=Depends(get_db)):
    # Get all events linked to a specific group
    rows = conn.execute("""
        SELECT 
            E.IDe, E.IDg, E.IsPublic, E.Position, E.Address, E.Description, E.Name, E.Size 
        FROM GroupEvents AS GE
        JOIN Event AS E ON GE.IDe = E.IDe
        WHERE GE.IDg = ?
    """, [group_id]).fetchall()

    return [
        {"IDe": r[0], "IDg": r[1], "IsPublic": r[2], "Position": r[3],
         "Address": r[4], "Description": r[5], "Name": r[6], "Size": r[7]}
        for r in rows
    ]

# ------------------ AUTH ENDPOINTS ------------------

@app.post("/login")
def login(req: LoginRequest, response: Response, conn=Depends(get_db)):
    if req.Username:
        row = conn.execute(
            'SELECT IDu, PasswordHash, Salt FROM "User" WHERE Username = ?',
            [req.Username]
        ).fetchone()
    elif req.IDu is not None:
        row = conn.execute(
            'SELECT IDu, PasswordHash, Salt FROM "User" WHERE IDu = ?',
            [req.IDu]
        ).fetchone()
    else:
        raise HTTPException(400, "Provide Username or IDu to login")

    if not row or not verify_password(req.Password, row[2], row[1]):
        raise HTTPException(401, "Invalid credentials")

    user_id = row[0]
    cookie = create_session(conn, user_id)
    response.set_cookie("session_cookie", cookie, httponly=True, max_age=604800)
    return {"message": "Logged in successfully"}


@app.post("/logout")
def logout(response: Response, session_cookie: Optional[str] = Cookie(None), conn=Depends(get_db)):
    if session_cookie:
        conn.execute("UPDATE Session SET IsLoggedIn = FALSE WHERE Cookie = ?", [session_cookie])
    response.delete_cookie("session_cookie")
    return {"message": "Logged out"}


# ------------------ EVENT ENDPOINTS ------------------

@app.post("/events", response_model=EventResponse)
def create_event(event: EventCreate, conn=Depends(get_db), user_id=Depends(get_current_user)):
    conn.execute("""
        INSERT INTO Event (IDg, IsPublic, Position, Address, Description, Name, Size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        event.IDg, event.IsPublic, event.Position, event.Address,
        event.Description, event.Name, event.Size
    ])

    id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    return {"IDe": id, **event.model_dump()}


@app.get("/events", response_model=list[EventResponse])
def list_events(conn=Depends(get_db), session_cookie: Optional[str] = Cookie(None)):
    # Try retrieving user; ignore if not logged in
    try:
        user_id = get_current_user(session_cookie=session_cookie, conn=conn)
    except:
        user_id = None

    if user_id:
        rows = conn.execute("SELECT * FROM Event").fetchall()
    else:
        rows = conn.execute("SELECT * FROM Event WHERE IsPublic = TRUE").fetchall()

    return [
        {"IDe": r[0], "IDg": r[1], "IsPublic": r[2], "Position": r[3],
         "Address": r[4], "Description": r[5], "Name": r[6], "Size": r[7]}
        for r in rows
    ]


@app.get("/events/{id}", response_model=EventResponse)
def get_event(id: int, conn=Depends(get_db)):
    row = conn.execute("SELECT * FROM Event WHERE IDe = ?", [id]).fetchone()
    if not row:
        raise HTTPException(404, "Event not found")
    if not row[2]:
        raise HTTPException(403, "Private event")

    return {"IDe": row[0], "IDg": row[1], "IsPublic": row[2], "Position": row[3],
            "Address": row[4], "Description": row[5], "Name": row[6], "Size": row[7]}


@app.delete("/events/{id}")
def delete_event(id: int, conn=Depends(get_db), user_id=Depends(get_current_user)):
    conn.execute("DELETE FROM Event WHERE IDe = ?", [id])
    return {"message": "Event deleted"}


# ------------------ RUN ------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
