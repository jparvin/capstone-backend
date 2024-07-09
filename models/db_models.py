from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.database_connection import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    AZURE_PERSONAL_ACCESS_TOKEN = Column(String)
    
    sessions = relationship('Session', back_populates='user')

    def update(self, data):
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(self, key, value)


class Session(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(Text, nullable=False)
    organization = Column(Text)
    project = Column(Text)
    project_name = Column(Text)
    
    user = relationship('User', back_populates='sessions')
    chats = relationship('Chat', back_populates='session')
    repositories = relationship('Repository', back_populates='session')
    files = relationship('File', back_populates='session')

class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False)
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    
    session = relationship('Session', back_populates='chats')


class Repository(Base):
    __tablename__ = 'repository'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False)
    name = Column(Text, nullable=False)
    repository_id = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    
    session = relationship('Session', back_populates='repositories')


class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text, nullable=False)
    path = Column(Text, nullable=False)
    category = Column(Text, nullable=False)

    session = relationship('Session', back_populates='repositories')