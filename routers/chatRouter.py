from fastapi import APIRouter, HTTPException, UploadFile, Depends
from models.request_bodies import ChatBody, ChatCreate, ChatResponse
from models.db_models import Chat
from utils.retrieve_data import ChatWithAI
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


####################
# Chat With Agents #
####################
@chatRouter.post("/generate")
def generate_chat(body: ChatBody, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        user_chat = Chat(session_id=body.session_id, role="user", content=body.message)
        chat_history = db.query(Chat).filter(Chat.session_id == body.session_id).all()
        chain = make_chain(body.user_id, body.session_id)
        response = chain.invoke({"input" : body.message, "chat_history": chat_history})
        ai_chat = Chat(session_id=body.session_id, role="ai", content=response['answer'])
        db.add(user_chat)
        db.add(ai_chat)
        db.commit()
        return ai_chat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chatRouter.post("/complex_generate")
async def generate_chat(body:ChatBody, db: Session = Depends(get_db)):
    response = await ChatWithAI(body.user_id, body.session_id, db=db).start_chain(body.message)
    return response

@chatRouter.post("/prompt")
async def test_prompt(body:ChatBody, db: Session = Depends(get_db)):
    response = await ChatWithAI(body.user_id, body.session_id, db=db).get_prompts(body.message)
    return response