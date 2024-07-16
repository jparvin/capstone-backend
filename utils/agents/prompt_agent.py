from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session
from models.db_models import File, Chat
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from typing import List
from models.other_models import InquiryFields
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain.memory import ChatMessageHistory


class Search(BaseModel):
    """Search over document queries, code queries and Azure Dev Ops queries"""

    queries: List[InquiryFields] = Field(
        description="Distinct queries for each type of search.",
    )

class QuestionScope(BaseModel):
    """Determine if more context is needed"""

    scope: bool = Field(
        description="True or False if more context for the question is needed",
    )


class PromptAgent:
    def __init__(self, model: ChatOpenAI, db: Session, session_id: int, user_id: int) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.model = model
        self.db = db

    def determine_scope(self, question: str) -> str:
        CONTEXT_PROMPT = """Given a chat history and the latest user question \
        which might reference context in the chat history, review if additional sources are needed.
        Only return true if you can answer the question based on the conversation history and the user question.
        Return false if more context is needed.
        Do NOT answer the prompt.
        Chat History:
        {chat_history}

        question:
        {input}
        """
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CONTEXT_PROMPT),
                ("human", "{input}")
            ])
        
        structured_model = self.model.with_structured_output(QuestionScope)
        query_analyzer = {"input": RunnablePassthrough(), "chat_history": RunnablePassthrough()} | contextualize_q_prompt | structured_model

        conversation_history = self.db.query(Chat).filter(Chat.session_id == self.session_id).all()
        chat_history= ChatMessageHistory()
        
        for chat in conversation_history:
            if chat.role == "AI":
                chat_history.add_ai_message(chat.content)
            else:
                chat_history.add_user_message(chat.content)        
        response = query_analyzer.invoke({"input": question, "chat_history": chat_history})
        return response.scope

    def parse_prompt(self, question:str) -> list[InquiryFields]:

        system = """
        Given the user question, retrieve which sources of data are relevant to the question. 
        Do not assume filenames functions or file types, only include them if they are explicitly mentioned in the question.
        You do not have to respond with a source if the question is general and does not reference a specific source.
        These sources include:
        - code: a specific code file. This includes references to a filename or a function within a file
        - repository: an azure dev ops repository or repository. This will include referencing multiple files or directories, or asking a general question about file strucutre.
        - documentation: documentation about program requirements or business logic

        You should respond in json format, with the following fields you can include multiple of each if necessary, but do not add any input before or after the json object. 
        For example, do not include any text like "Here is the relevant information:".
        
        Do not assume filenames functions or file types, only include them if they are explicitly mentioned in the question.
        You do not have to respond with a source if the question is general and does not reference a specific source.

        Here are all of the documentation sources you can reference:
        {documentation_sources}

        Here are all of the code file sources you can reference:
        {code_sources}

        Be creative with the inquiry and make each inquiry unique to the type of source.

        <question>
        {question}
        </question>
        
        Output:
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "{question}")
            ]
        )
        output_parser = PydanticToolsParser(tools=[Search])

        doc_files = self.db.query(File).filter(File.session_id == self.session_id and File.category == 'documentation').all()
        doc_file_names="\n".join([file.filename for file in doc_files])

        code_files = self.db.query(File).filter(File.session_id == self.session_id and File.category == 'code').all()
        code_file_names="\n".join([file.filename for file in code_files])

        structured_model = self.model.with_structured_output(Search)

        query_analyzer = {"question" : RunnablePassthrough(), "code_sources" : RunnablePassthrough(), "documentation_sources": RunnablePassthrough()} | prompt | structured_model

        response = query_analyzer.invoke({"question": question, "code_sources": code_file_names, "documentation_sources": doc_file_names})

        
        return response.queries

