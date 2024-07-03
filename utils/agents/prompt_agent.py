from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json

def parse_prompt(question, model:ChatOpenAI):

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
    chain = (
        PromptTemplate.from_template(template) | model | StrOutputParser()
    )
    response = chain.invoke({"question": question})
    response_json = json.loads(response)
    return response_json