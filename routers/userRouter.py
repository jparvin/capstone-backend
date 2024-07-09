from fastapi import APIRouter, HTTPException, Depends
from models.request_bodies import UserCreate, UserUpdate, UserResponse, UserLogin
from models.db_models import User, SessionModel
from sqlalchemy.orm import Session
from database.database_connection import session

def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()

userRouter =  APIRouter()

@userRouter.post("/login")
def login_user(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password != body.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    sessions = db.query(SessionModel).filter(SessionModel.user_id == user.id).all()
    user_dict = user.to_dict()
    user_dict['sessions'] = [session.to_dict() for session in sessions]
    return user_dict

@userRouter.post("/create")
def create_user(body: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    print(body.model_dump())
    user = User(**body.model_dump())
    db.add(user)
    db.commit()
    new_session = SessionModel(**{'user_id': user.id, 'name': 'Default Session'})
    db.add(new_session)
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