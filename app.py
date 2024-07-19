from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chatRouter import chatRouter
from routers.azureRouter import azureRouter
from routers.fileRouter import fileRouter
from routers.userRouter import userRouter
from routers.sessionRouter import sessionRouter
from database.database_connection import engine
from models.db_models import Base
from database.sqlite.Test_Data.test_data import load_data

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:3000"],  # Adjust this to the URL of your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/load_data")
def load_sample_data():
    load_data()
    return {"message": "Data loaded successfully"}

app.include_router(chatRouter, prefix="/chat", tags=["Chat"])
app.include_router(azureRouter, prefix="/azure", tags=["Azure"])
app.include_router(fileRouter, prefix="/file", tags=["Files"])
app.include_router(userRouter, prefix="/user", tags=["Users"])
app.include_router(sessionRouter, prefix="/session", tags=["Sessions"])