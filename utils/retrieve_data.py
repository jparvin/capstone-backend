from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from .agents.prompt_agent import PromptAgent
from .agents.documentation_agent import query_documentation
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = "gpt-4o"
TEMPERATURE = 0.1
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

class CodeAgent:
    def __init__(self, user_id:int, session_id:int, db:Session) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.db = db
        self.model = ChatOpenAI(temperature=TEMPERATURE, model=MODEL, api_key=OPENAI_API_KEY)
    
    def change_model(self, model:str = MODEL, temp:float = TEMPERATURE):
        self.model = ChatOpenAI(temperature=temp, model=model, api_key=OPENAI_API_KEY)
        return self.model

    def start_chain(self, question):
        promptAgent = PromptAgent(self.model, self.db, self.session_id, self.user_id)
        return promptAgent.parse_prompt_documentation(question)
        

    def chat_documentation(self, inquiry:str, file:str = None):
        if file:
            return query_documentation(file, inquiry, self.change_model(model='gpt-4o'), self.user_id, self.session_id)
        