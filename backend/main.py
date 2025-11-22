from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
import secrets


from models import (
    create_db_and_tables,
    User, Group, Event, Session as SessionModel,
    generate_salt, hash_password, verify_password
)
from database import get_session
from schemas import (
    UserCreate, UserUpdate, UserResponse, UserLogin, LoginResponse,
    GroupCreate, GroupResponse,
    EventCreate, EventUpdate, EventResponse
)


app = FastAPI(title="MadEvents API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# ============== USER ROUTES ==============

@app.post("/users", response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_session)):
    salt = generate_salt()
    hashed = hash_password(user_data.Password, salt)
    user = User(
        IDg=user_data.IDg,
        privilege=user_data.Privilege,
        Password=hashed,
        Salt=salt
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_session)):
    return db.exec(select(User)).all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, val in user_data.model_dump(exclude_unset=True).items():
        setattr(user, key, val)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"deleted": True}


# ============== AUTH ROUTES ==============

@app.post("/login", response_model=LoginResponse)
def login(creds: UserLogin, db: Session = Depends(get_session)):
    user = db.get(User, creds.IDu)
    if not user or not verify_password(creds.Password, user.Salt, user.Password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    cookie = secrets.token_urlsafe(32)
    session = SessionModel(Cookie=cookie, IDu=user.IDu, IsLoggedIn=True)
    db.add(session)
    db.commit()
    return {"cookie": cookie, "user_id": user.IDu}


@app.post("/logout")
def logout(cookie: str, db: Session = Depends(get_session)):
    session = db.get(SessionModel, cookie)
    if session:
        db.delete(session)
        db.commit()
    return {"logged_out": True}


@app.get("/me", response_model=UserResponse)
def get_current_user(cookie: str, db: Session = Depends(get_session)):
    session = db.get(SessionModel, cookie)
    if not session or not session.IsLoggedIn:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session.user


# ============== GROUP ROUTES ==============

@app.post("/groups", response_model=GroupResponse)
def create_group(group_data: GroupCreate, db: Session = Depends(get_session)):
    group = Group(Name=group_data.Name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@app.get("/groups", response_model=List[GroupResponse])
def get_groups(db: Session = Depends(get_session)):
    return db.exec(select(Group)).all()


@app.get("/groups/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_session)):
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@app.delete("/groups/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_session)):
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()
    return {"deleted": True}


# ============== EVENT ROUTES ==============

@app.post("/events", response_model=EventResponse)
def create_event(event_data: EventCreate, db: Session = Depends(get_session)):
    event = Event(**event_data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.get("/events", response_model=List[EventResponse])
def get_events(
    public_only: bool = False,
    group_id: int = None,
    db: Session = Depends(get_session)
):
    query = select(Event)
    if public_only:
        query = query.where(Event.IsPublic == True)
    if group_id:
        query = query.where(Event.IDg == group_id)
    return db.exec(query).all()


@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_session)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.patch("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_data: EventUpdate, db: Session = Depends(get_session)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, val in event_data.model_dump(exclude_unset=True).items():
        setattr(event, key, val)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_session)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"deleted": True}