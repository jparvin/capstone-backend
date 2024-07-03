import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from database.vector_store import get_pinecone
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def make_chain(
    user_id, session_id
) -> RunnableParallel:
    try:
        MODEL = "gpt-3.5-turbo-0125"
        TEMPERATURE = 0.1
        CONTEXT_PROMPT = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

        PROMPT = """
        You are a web developer who is an expert in a multitude of programming language. You are to give helpful answers to users who are asking
        questions about a code repository. You should understand the code given to you, and answer the user's question as best as possible.

        Here is the conversation history:
        {chat_history}

        Anything between the following `context`  html blocks is retrieved from a knowledge bank, not part of the conversation with the user
        <context>
            {context} 
        <context/>

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
        pinecone = get_pinecone(namespace=f"{user_id}_{session_id}")
        
        retriever = pinecone.as_retriever()
        model = ChatOpenAI(temperature=TEMPERATURE, model=MODEL, api_key=OPENAI_API_KEY)
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXT_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
        )
        history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ]
        )   

        question_answer_chain = create_stuff_documents_chain(model, prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        return rag_chain
    except Exception as e:
        print(e)
        raise e


def format_conversation(conversation_history:dict):
    chat_history = []
    for chat in conversation_history:
        chat_history.append({chat["role"] : chat["content"]})
    return chat_history

