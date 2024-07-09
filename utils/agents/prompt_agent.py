from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json

def parse_prompt(question, model:ChatOpenAI):

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
        PromptTemplate.from_template(template) | model | StrOutputParser()
    )
    response = chain.invoke({"question": question})
    response_json = json.loads(response)
    return response_json

def parse_prompt_documentation(question, model:ChatOpenAI):

    template = """
    You are a code developer that is an expert in documentation and translation of business requests to code.
    You will be presented with a question and need to determine if any of the given filenames would be relevant to the question.
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