from pydantic import BaseModel, EmailStr
from typing import List, Optional

class ChatBody(BaseModel):
    user_id: int
    session_id: int
    message: str

class UserSession(BaseModel):
    user_id: int
    session_id: int


class UserBase(BaseModel):
    email: EmailStr
    password: str
    AZURE_PERSONAL_ACCESS_TOKEN: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    AZURE_PERSONAL_ACCESS_TOKEN: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class SessionBase(BaseModel):
    user_id: int
    name: str
    organization: Optional[str] = None
    project: Optional[str] = None
    project_name: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionUpdate(SessionBase):
    user_id: Optional[int] = None
    name: Optional[str] = None
    organization: Optional[str] = None
    project: Optional[str] = None
    project_name: Optional[str] = None



class ChatBase(BaseModel):
    session_id: int
    role: str
    content: str

class ChatCreate(ChatBase):
    pass

class ChatMetadata(BaseModel):
    source: str
    type: str

class ChatContext(BaseModel):
    id: int = None
    metadata: ChatMetadata
    page_content: str
    type: str

class ChatDocumentationResponse(BaseModel):
    context: List[ChatContext]
    question : str
    answer : str

class ChatResponse(ChatBase):
    id: int

    class Config:
        orm_mode = True

class RepositoryBase(BaseModel):
    session_id: int
    name: str
    repository_id: str
    url: str

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryUpdate(RepositoryBase):
    session_id: Optional[int] = None
    name: Optional[str] = None
    repository_id: Optional[str] = None
    url: Optional[str] = None

class RepositoryResponse(RepositoryBase):
    id: int

    class Config:
        orm_mode = True

class FileBase(BaseModel):
    filename:str
    category:str

class FileCreate(BaseModel):
    user_id: int
    session_id: int
    category: str

class FileUpdate(FileBase):
    filename: Optional[str] = None
    category: Optional[str] = None

class FileResponse(FileBase):
    id: int

    class Config:
        orm_mode = True

class SessionResponse(SessionBase):
    id: int
    files: List[FileResponse]
    chats: List[ChatResponse]
    repositories: List[RepositoryResponse]

    class Config:
        orm_mode = True

class UserLoginResponse(UserBase):
    user: UserResponse
    session: List[SessionResponse]

    class Config:
        orm_mode = True