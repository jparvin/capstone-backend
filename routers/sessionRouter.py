from fastapi import APIRouter, HTTPException, Depends
from models.request_bodies import SessionCreate, SessionUpdate, SessionResponse
from models.db_models import SessionModel, File
from sqlalchemy.orm import Session
from database.database_connection import session
from utils.doc_manager import delete_file_from_pinecone
def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()

sessionRouter = APIRouter()

@sessionRouter.post("/create", response_model=SessionResponse)
def create_session(body: SessionCreate, db: Session = Depends(get_db)) -> SessionResponse:
    try:
        db_session = SessionModel(**body.model_dump())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@sessionRouter.get("/get/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)) -> SessionResponse:
    try:
        db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        return db_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@sessionRouter.patch("/update/{session_id}", response_model=SessionResponse)
def update_session(session_id: int, body: SessionUpdate, db: Session = Depends(get_db)) -> SessionResponse:
    try:
        db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(db_session, key, value)
        db.commit()
        db.refresh(db_session)
        return db_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@sessionRouter.delete("/delete/{session_id}") 
def delete_session(session_id: int, db: Session = Depends(get_db)) -> SessionResponse:
    try:
        db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        files = db.query(File).filter(File.session_id == session_id).all()
        for file in files:
            delete_file_from_pinecone(file.filename, db_session.user_id, db_session.id)
        db.delete(db_session)
        db.commit()
        return "success"
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))