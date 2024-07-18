from langchain_aws import ChatBedrock
from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from models.db_models import  Chat
from sqlalchemy.orm import Session
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough

def conversation_chat(
    chat_history: ChatMessageHistory, session_id:int, question:str,  model:ChatBedrock
) -> RunnableParallel:
    try:

        PROMPT = """
        You are a web developer who is an expert in a multitude of programming language. You are to give helpful answers to users who are asking
        questions about a code repository. You should understand the code given to you, and answer the user's question as best as possible.

        Here is the conversation history:
        {chat_history}

        Question: {input}
        Please provide answers formatted in Markdown.
        Please refrain from including any text before or after the providing Markdown content to maintain clean formatting. For example, do not include any text like "Certainly, here's an explanation of an RFQ in Markdown format:".
        If you are generating Markdown output, ensure that it reflects a professional and polished appearance suitable for sales proposals. You can use Markdown syntax such as headers, paragraphs, lists, etc., but avoid unnecessary formatting. For example:
        # Key Features
        - Feature 1
        - Feature 2
        
        NEVER REPLY IN CODE markdown FORMAT.
        REMEMBER: If there is no relevant information within the context ask a clarifying question.
        
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT),
                ("human", "{input}")
            ]
        )   
        
        query = {"input": RunnablePassthrough(), "chat_history": RunnablePassthrough()} | prompt | model
        print(chat_history)
        response = query.invoke({"chat_history": chat_history, "input": question})
        return response.content
    except Exception as e:
        print(e)
        raise e

