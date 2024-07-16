from models.other_models import InquiryFields, SourceTypes
from langchain_openai import ChatOpenAI
from .agents.prompt_agent import PromptAgent
from .agents.review_agent import ReviewAgent
from .agents.documentation_agent import query_documentation
from .agents.code_agent import query_code
from sqlalchemy.orm import Session
from models.request_bodies import ChatDocumentationResponse
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = "gpt-4o"
TEMPERATURE = 0.1
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

class ChatWithAI:
    def __init__(self, user_id:int, session_id:int, db:Session) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.db = db
        self.model = ChatOpenAI(temperature=TEMPERATURE, model=MODEL, api_key=OPENAI_API_KEY)
    
    def change_model(self, model:str = MODEL, temp:float = TEMPERATURE):
        self.model = ChatOpenAI(temperature=temp, model=model, api_key=OPENAI_API_KEY)
        return self.model

    def get_prompts(self, question):
        promptAgent = PromptAgent(self.model, self.db, self.session_id, self.user_id)
        return promptAgent.parse_prompt(question)

    async def start_chain(self, question):
        promptAgent = PromptAgent(self.model, self.db, self.session_id, self.user_id)
        queries = promptAgent.parse_prompt(question)
        documentation_responses:list[ChatDocumentationResponse] = []
        code_responses:list[ChatDocumentationResponse] = []
        for query in queries:
            source = query.source
            inquiry = query.inquiry
            files = query.files
            if source == SourceTypes.documentation:
                response = await query_documentation(
                    files, 
                    inquiry, 
                    self.change_model(model='gpt-4o'), 
                    self.user_id, 
                    self.session_id
                )
                documentation_responses.append(response)
            elif source == SourceTypes.code:
                response = await query_code(
                    files, 
                    inquiry, 
                    self.change_model(model='gpt-4o'), 
                    self.user_id, 
                    self.session_id
                )
                code_responses.append(response)
        
        masterAgent = ReviewAgent(self.model)
        response = masterAgent.review_sources(original_question=question, documentation_responses=documentation_responses, code_responses=code_responses)
        return {"response" : response, "documentation_responses" :  documentation_responses, "code_responses" : code_responses}

    def chat_documentation(self, inquiry:str, file:str = None) -> ChatDocumentationResponse:
        if file:
            return query_documentation(file, inquiry, self.change_model(model='gpt-4o'), self.user_id, self.session_id)
    