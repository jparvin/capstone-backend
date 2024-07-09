from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from .agents.prompt_agent import parse_prompt
from .agents.documentation_agent import query_documentation
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = "gpt-3.5-turbo-0125"
TEMPERATURE = 0.1
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

class CodeAgent:
    def __init__(self, user_id:int, session_id:int) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.model = ChatOpenAI(temperature=TEMPERATURE, model=MODEL, api_key=OPENAI_API_KEY)
    
    def change_model(self, model:str = MODEL, temp:float = TEMPERATURE):
        self.model = ChatOpenAI(temperature=temp, model=model, api_key=OPENAI_API_KEY)
        return self.model

    def start_chain(self, question):
        response_json = parse_prompt(question, self.model)
        print(response_json)
        responses = []
        for item in response_json:
            if item['source'] == 'clarification':
                return {"answer" : item['inquiry']}
            if item['source'] == 'code':
                print(f"Code source: {item['name']}")
                responses.append(item)
            elif item['source'] == 'repository':
                responses.append(item)
                print(f"Repository source: {item['inquiry']}")
            elif item['source'] == 'documentation':
                responses.append({"documentation_response" : self.chat_documentation(file=item['name'], inquiry=item['inquiry'])})
        return responses
        

    def chat_documentation(self, inquiry:str, file:str = None):
        if file:
            return query_documentation(file, inquiry, self.change_model(model='gpt-4o'), self.user_id, self.session_id)
        