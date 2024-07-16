from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json
from models.request_bodies import ChatDocumentationResponse


class ReviewAgent:
    def __init__(self, model: ChatOpenAI) -> None:
        self.model = model
    
    def review_sources(self, original_question:str, documentation_responses:list[ChatDocumentationResponse], code_responses:list[ChatDocumentationResponse]):
        PROMPT = """
        You are an all around expert in code development and documentation. 
        You have been provided with a list of responses from a code developer and product manager that is an expert in documentation and translation of business requests to code.
        You will need to review the responses and determine if the responses are relevant to the original question asked.
        After reviewing the responses, I want you to answer the original question with all of the relevant information given.
        
        Here are the responses and sources gathered from the code developer:
        {code_responses}

        Here are the responses and sources gathered from the product manager on business documentation:
        {documentation_responses}

        Here is the original question:
        {question}

        Please provide answers formatted in Markdown.
        Please refrain from including any text before or after the providing Markdown content to maintain clean formatting. For example, do not include any text like "Certainly, here's an explanation of an RFQ in Markdown format:".
        If you are generating Markdown output, ensure that it reflects a professional and polished appearance suitable for sales proposals. You can use Markdown syntax such as headers, paragraphs, lists, etc., but avoid unnecessary formatting. For example:
        # Key Features
        - Feature 1
        - Feature 2

        NEVER REPLY IN CODE markdown FORMAT.
        Helpful Answer:  
        """
        custom_prompt = PromptTemplate.from_template(PROMPT)
        chain = (
            custom_prompt | self.model | StrOutputParser()
        )

        response = chain.invoke({"question": original_question, "documentation_responses": documentation_responses, "code_responses": code_responses})
        return response