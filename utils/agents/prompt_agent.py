from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = "gpt-3.5-turbo-0125"
TEMPERATURE = 0.1
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def parse_prompt(question):

    template = """
    Given the user question, retrieve which sources of data are relevant to the question. These sources include:
    - code: a specific code file. This includes references to a filename or a function within a file
    - repository: an azure dev ops repository or repository. This will include referencing multiple files or directories, or asking a general question about file strucutre.
    - documentation: documentation about program requirements or business logic

    You should respond in json format, with the following fields you can include multiple of each if necessary, but do not add any input before or after the json object. 
    For example, do not include any text like "Here is the relevant information:".
    Do not assume filenames functions or file types, only include them if they are explicitly mentioned in the question.
    Be creative with the inquiry
    [

            "source": "code",
            "file": "",
            "file_type(s)": [] or None,
            "function_name": "",
            "inquiry" : "question to ask about the function"
        ,
        
            "source": "repository",
            "inquiry" : "question to ask about the repository"
        ,
        
            "source": "documentation",
            "file": ""
            "inquiry" : "information to ask about the documentation",
        
    ]

    <question>
    {question}
    </question>
    Output:
    """
    model = ChatOpenAI(temperature=TEMPERATURE, model=MODEL, api_key=OPENAI_API_KEY)

    chain = (
        PromptTemplate.from_template(template) | model | StrOutputParser()
    )
    response = chain.invoke({"question": question})
    print(response)
    response_json = json.loads(response)
    print(response_json)
    return response_json

parse_prompt("In the OneWarehouseMobile - Warehouse Returns documentation it mentions the need to insert records into an Inventory_Transfer_GL table. This is likely done in a stored procedure slq file. Where would I find the function that does that?")