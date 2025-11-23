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
            IDg INTEGER REFERENCES "Group"(IDg),
            Privilege VARCHAR DEFAULT 'user',
            Username VARCHAR,
            PasswordHash VARCHAR NOT NULL,
            Salt VARCHAR NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Event (
            IDe INTEGER PRIMARY KEY,
            IDg INTEGER REFERENCES "Group"(IDg),
            IsPublic BOOLEAN DEFAULT TRUE,
            Position VARCHAR,
            Address VARCHAR,
            Description TEXT,
            Name VARCHAR NOT NULL,
            Size INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Session (
            Cookie VARCHAR PRIMARY KEY,
            IDu INTEGER REFERENCES "User"(IDu),
            IsLoggedIn BOOLEAN DEFAULT TRUE,
            ExpiresAt TIMESTAMP
        )
    """)
    # Create sequences for auto-increment
    conn.execute("CREATE SEQUENCE IF NOT EXISTS user_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS group_seq START 1")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS event_seq START 1")
    conn.close()

    # Migration: ensure Username column exists for older databases
    conn = duckdb.connect(DB_PATH)
    try:
        cols = conn.execute("PRAGMA table_info('User')").fetchall()
        col_names = [c[1] for c in cols]
        if 'Username' not in col_names:
            conn.execute('ALTER TABLE "User" ADD COLUMN Username VARCHAR')
            # Backfill usernames from IDu so existing users have deterministic usernames
            conn.execute('UPDATE "User" SET Username = "user" || IDu WHERE Username IS NULL')
    except Exception:
        # If migration fails, continue; app will enforce username uniqueness on create
        pass
    finally:
        conn.close()

# --- Pydantic Models ---
class GroupCreate(BaseModel):
    Name: str

class GroupResponse(BaseModel):
    IDg: int
    Name: str

class UserCreate(BaseModel):
    IDg: Optional[int] = None
    Privilege: str = "user"
    Username: str
    Password: str

class UserResponse(BaseModel):
    IDu: int
    IDg: Optional[int]
    Privilege: str
    Username: Optional[str]

class EventCreate(BaseModel):
    IDg: Optional[int] = None
    IsPublic: bool = True
    Position: Optional[str] = None
    Address: Optional[str] = None
    Description: Optional[str] = None
    Name: str
    Size: Optional[int] = None

class EventResponse(BaseModel):
    IDe: int
    IDg: Optional[int]
    IsPublic: bool
    Position: Optional[str]
    Address: Optional[str]
    Description: Optional[str]
    Name: str
    Size: Optional[int]

class LoginRequest(BaseModel):
    IDu: Optional[int] = None
    Username: Optional[str] = None
    Password: str

# --- Auth Helpers ---
def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, salt: str, hash: str) -> bool:
    return hash_password(password, salt) == hash

def create_session(conn, user_id: int) -> str:
    cookie = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(days=7)
    conn.execute(
        "INSERT INTO Session (Cookie, IDu, IsLoggedIn, ExpiresAt) VALUES (?, ?, TRUE, ?)",
        [cookie, user_id, expires]
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

@app.post("/groups", response_model=GroupResponse)
def create_group(group: GroupCreate, conn=Depends(get_db)):
    conn.execute('INSERT INTO "Group" (Name) VALUES (?)', [group.Name])
    id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {"IDg": id, "Name": group.Name}


@app.get("/groups", response_model=list[GroupResponse])
def list_groups(conn=Depends(get_db)):
    rows = conn.execute('SELECT IDg, Name FROM "Group"').fetchall()
    return [{"IDg": r[0], "Name": r[1]} for r in rows]


@app.get("/groups/{id}", response_model=GroupResponse)
def get_group(id: int, conn=Depends(get_db)):
    row = conn.execute('SELECT IDg, Name FROM "Group" WHERE IDg = ?', [id]).fetchone()
    if not row:
        raise HTTPException(404, "Group not found")
    return {"IDg": row[0], "Name": row[1]}


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
