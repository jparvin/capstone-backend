from sqlalchemy import Column, Integer, String, Text
from database.database_connection import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    AZURE_PERSONAL_ACCESS_TOKEN = Column(String)