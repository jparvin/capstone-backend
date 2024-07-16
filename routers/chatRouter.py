from fastapi import APIRouter, HTTPException, UploadFile, Depends
from models.request_bodies import ChatBody, ChatCreate, ChatResponse
from models.db_models import Chat
from utils.retrieve_data import ChatWithAI
from utils.agents.test_agent import make_chain
from sqlalchemy.orm import Session
import openai
from database.database_connection import session
from utils.agents.langgraph import Graph

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
    user_chat = Chat(session_id=body.session_id, role="user", content=body.message)
    response = ChatWithAI(body.user_id, body.session_id, db=db).start_chain(body.message)
    ai_chat = Chat(session_id=body.session_id, role="ai", content=response['response'])
    db.add(user_chat)
    db.add(ai_chat)
    db.commit()
    return ai_chat

@chatRouter.post("/complex_generate_sources")
async def generate_chat(body:ChatBody, db: Session = Depends(get_db)):
    user_chat = Chat(session_id=body.session_id, role="user", content=body.message)
    response = ChatWithAI(body.user_id, body.session_id, db=db).start_chain_only_sources(body.message)
    ai_chat = Chat(session_id=body.session_id, role="ai", content=response['response'])
    db.add(user_chat)
    db.add(ai_chat)
    print(ai_chat)
    print(user_chat)
    db.commit()
    return response

@chatRouter.post("/prompt")
async def test_prompt(body:ChatBody, db: Session = Depends(get_db)):
    response = ChatWithAI(body.user_id, body.session_id, db=db).get_prompts(body.message)
    return response

@chatRouter.post("/test_graph")
def test_graph(body:ChatBody, db:Session = Depends(get_db)):
    response = Graph(body.user_id, body.session_id, db).agent_setup()
    return {"message" : "complete"}