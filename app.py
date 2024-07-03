from fastapi import FastAPI
from routers.router import chatRouter, azureRouter, pineconeRouter

app = FastAPI()
app.include_router(chatRouter, prefix="/chat", tags=["Chat"])
app.include_router(azureRouter, prefix="/azure", tags=["Azure"])
app.include_router(pineconeRouter, prefix="/DB", tags=["Database"])