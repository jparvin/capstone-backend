from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .sqlite.create_db import create
import os
DATABASE_URL="sqlite:///database/sqlite/chatbot.db"
if not os.path.exists("database/sqlite/chatbot.db"):
    create()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()