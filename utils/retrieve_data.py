from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from agents import prompt_agent
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = "gpt-3.5-turbo-0125"
TEMPERATURE = 0.1
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

class CodeAgent:
    def __init__(self, organization:str, project:str) -> None:
        self.organization = organization
        self.project = project
        self.model = ChatOpenAI(temperature=TEMPERATURE, model=MODEL, api_key=OPENAI_API_KEY)

    def start_chain(self, question):
        response_json = prompt_agent.parse_prompt(question)
        for item in response_json:
            if item['source'] == 'code':
                print(f"Code source: {item['file']}")
            elif item['source'] == 'repository':
                print(f"Repository source: {item['inquiry']}")
            elif item['source'] == 'documentation':
                self.documentation_inqury(item['file'], item['inquiry'])
        return response_json

        