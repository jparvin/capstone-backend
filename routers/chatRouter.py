from fastapi import APIRouter, HTTPException, UploadFile, Depends
from models.request_bodies import ChatBody, ChatCreate, ChatResponse
from utils.retrieve_data import CodeAgent
from utils.agents.test_agent import make_chain
from sqlalchemy.orm import Session
import openai
from database.database_connection import session

def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()
        
client = openai.OpenAI()
chatRouter =  APIRouter()
chat_history = []


####################
# Chat With Agents #
####################
@chatRouter.post("/generate")
def generate_chat(body: ChatBody, db: Session = Depends(get_db)):
    chain = make_chain(body.user_id, body.session_id)
    response = chain.invoke({"input" : body.message, "chat_history": chat_history})
    chat_history.append({"role": "assistant", "content": response['answer']})
    return {"data" : response['answer']}

@chatRouter.post("/complex_generate")
def generate_chat(body:ChatBody, db: Session = Depends(get_db)):
    response = CodeAgent(body.user_id, body.session_id).start_chain(body.message)
    return response
