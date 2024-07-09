from pydantic import BaseModel

class ChatBody(BaseModel):
    user_id: int
    session_id: int
    message: str

class UserSession(BaseModel):
    user_id: int
    session_id: int


class UserBase(BaseModel):
    username: str
    email: str
    password: str
    AZURE_PERSONAL_ACCESS_TOKEN: str

class UserCreate(BaseModel):
    pass 

class User(UserBase):
    id:int
    class Config:
        orm_mode = True