from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session
from models.db_models import File
import json

class PromptAgent:
    def __init__(self, model:ChatOpenAI, db:Session, session_id:int, user_id:int) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.model = model
        self.db = db

    def parse_prompt(self, question:str):

        template = """
        Given the user question, retrieve which sources of data are relevant to the question. 
        Do not assume filenames functions or file types, only include them if they are explicitly mentioned in the question.
        You do not have to respond with a source if the question is general and does not reference a specific source.
        These sources include:
        - code: a specific code file. This includes references to a filename or a function within a file
        - repository: an azure dev ops repository or repository. This will include referencing multiple files or directories, or asking a general question about file strucutre.
        - documentation: documentation about program requirements or business logic

        You should respond in json format, with the following fields you can include multiple of each if necessary, but do not add any input before or after the json object. 
        For example, do not include any text like "Here is the relevant information:".
        
        Be creative with the inquiry
        [

                "source": "code | repository | documentation",
                "name": "filename | function | repository name",
                "inquiry": "question"
            
        ]
        If no relevant sources are found, return a clarifying question. In the format:
        [
            "source": "clarification",
            "inquiry": "clarifying question"
        ]
        Do not assume filenames functions or file types, only include them if they are explicitly mentioned in the question.
        You do not have to respond with a source if the question is general and does not reference a specific source.
        <question>
        {question}
        </question>
        Output:
        """
        chain = (
            PromptTemplate.from_template(template) | self.model | StrOutputParser()
        )
        response = chain.invoke({"question": question})
        response_json = json.loads(response)
        return response_json

    def parse_prompt_documentation(self, question:str):

        template = """
        You are a code developer that is an expert in documentation and translation of business requests to code.
        You will be presented with a question and need to determine if any of the given filenames would be relevant to the question.
        If the question is general and does not reference a specific filename, you do not need to include any filenames in your response.
        Here are the files currently uploaded to the system:
        <files>
        {files}
        </files>
        Here is the user question:
        <question>
        {question}
        </question>

        Please respond in json format, with the following fields for each filename that is relevant to the question:
        [
            "filename": "filename",
            "inquiry": "question"
        ]
        Output:
        """
        files = self.db.query(File).filter(File.session_id == self.session_id and File.category == 'documentation').all()
        file_names=[file.filename for file in files]
        custom_prompt = PromptTemplate.from_template(template)
        custom_prompt = custom_prompt.assign(files=",".join(file_names))
        chain = (
            custom_prompt | self.model | StrOutputParser()
        )

        response = chain.invoke({"question": question})
        response_json = json.loads(response)
        print(response_json)
        return response_json