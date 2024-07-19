from fastapi import APIRouter, HTTPException, UploadFile, Depends, Form, File
import shutil
from utils.doc_manager import upload_doc_to_pinecone, delete_file_from_pinecone
from models.request_bodies import FileCreate, FileUpdate, FileResponse
from models.db_models import File as DbFile, SessionModel
from sqlalchemy.orm import Session
import os
from database.database_connection import session

def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()

fileRouter =  APIRouter()

ALLOWED_EXTENSIONS = {'txt', 'doc', 'sql', 'py', 'cs', 'docx', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


####################
# File Management  #
####################
async def get_file_metadata(
    session_id: int = Form(...),
    user_id: int = Form(...),
    category: str = Form(...)
):
    return FileCreate(session_id=session_id, user_id=user_id, category=category)

@fileRouter.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    body: FileCreate = Depends(get_file_metadata),
    db: Session = Depends(get_db)
    ) -> FileResponse:
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No file uploaded")
    if allowed_file(file.filename.split('.')[-1]):
        raise HTTPException(status_code=400, detail="File type not allowed")
    #try:
    filepath = os.path.join(os.getcwd(), "documents", file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    session = db.query(SessionModel).filter(SessionModel.id == body.session_id).first()
    docs = upload_doc_to_pinecone(filepath, namespace=session.pinecone, category=body.category)
    db_file = DbFile(filename=file.filename, category=body.category, session_id=body.session_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    os.remove(filepath)
    return db_file
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail=str(e))

@fileRouter.get("/{file_name}", response_model=FileResponse)
def get_file(file_name: str, db: Session = Depends(get_db)) -> FileResponse:
    try:
        db_file = db.query(DbFile).filter(DbFile.filename == file_name).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        return db_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fileRouter.patch("/{file_id}", response_model=FileResponse)
def update_file(file_id: int, body: FileUpdate, db: Session = Depends(get_db)) -> FileResponse:
    try:
        db_file = db.query(DbFile).filter(DbFile.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(db_file, key, value)
        db.commit()
        db.refresh(db_file)
        return db_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@fileRouter.delete("/{file_name}", response_model=dict)
def delete_file(file_name: str, db: Session = Depends(get_db)):
    db_file = db.query(DbFile).filter(DbFile.filename == file_name).all()
    if db_file.count(DbFile) is 0:
        raise HTTPException(status_code=404, detail="File not found")
    db_session = db.query(SessionModel).filter(SessionModel.id == db_file[0].session_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    status=delete_file_from_pinecone(file_name, db_session.pinecone)
    db.delete(db_file)
    db.commit()
    return {"message": status}