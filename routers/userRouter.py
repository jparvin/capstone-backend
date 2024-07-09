from fastapi import APIRouter, HTTPException, Depends
from models.request_bodies import UserCreate, UserUpdate, UserResponse, UserLogin, UserLoginResponse
from models.db_models import User
from sqlalchemy.orm import Session
from database.database_connection import session

def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()

userRouter =  APIRouter()

@userRouter.get("/login")
def login_user(body: UserLogin, db: Session = Depends(get_db)) -> UserLoginResponse:
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password != body.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    sessions = db.query(Session).filter(Session.user_id == user.id).all()
    return {'user' : user, 'session' : sessions}

@userRouter.post("/create")
def create_user(body: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(**body.model_dump())
    db.add(user)
    db.commit()
    return user

@userRouter.patch("/update/{user_id}")
def update_user(user_id:int, body: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.update(body.model_dump())
    db.commit()
    return user