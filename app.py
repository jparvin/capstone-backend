from fastapi import FastAPI
from routers.chatRouter import chatRouter
from routers.azureRouter import azureRouter
from routers.fileRouter import fileRouter
from routers.userRouter import userRouter
from routers.sessionRouter import sessionRouter
from database.database_connection import engine
from models.db_models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(chatRouter, prefix="/chat", tags=["Chat"])
app.include_router(azureRouter, prefix="/azure", tags=["Azure"])
app.include_router(fileRouter, prefix="/file", tags=["Files"])
app.include_router(userRouter, prefix="/user", tags=["Users"])
app.include_router(sessionRouter, prefix="/session", tags=["Sessions"])