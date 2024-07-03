from pydantic import BaseModel

class ChatBody(BaseModel):
    user_id: int
    session_id: int
    message: str

class UserSession(BaseModel):
    user_id: int
    session_id: int