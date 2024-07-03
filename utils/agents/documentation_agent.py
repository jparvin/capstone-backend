import os, glob, difflib
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, Runnable
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from database.vector_store import get_langchain_pinecone

def query_documentation(filename:str, inquiry:str, model:ChatOpenAI, user_id:int, session_id:int):
    try:
        PROMPT = """
        You are a developer that is an expert in documentation and translation of business requests to code. 
        You will be provided with documentation about a given topic, and will need to answer questions about it.


        Anything between the following `context`  html blocks is retrieved from a knowledge bank, not part of the conversation with the user
        <context>
            {context} 
        <context/>

        Question: {question}

        Helpful Answer:  
        """
        pinecone:PineconeVectorStore = get_langchain_pinecone(namespace=f"{user_id}_{session_id}")
        doc = get_closest_file_match(filename)
        print(doc)
        print(inquiry)
        retriever = pinecone.as_retriever(
            search_kwargs={'filter': {'source':doc}}
        )

        custom_rag_prompt = PromptTemplate.from_template(PROMPT)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | custom_rag_prompt
            | model
            | StrOutputParser()
        )
        
        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
            | custom_rag_prompt
            | model
            | StrOutputParser()
        )

        rag_chain_with_source = RunnableParallel(
            {"context": retriever, "question": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)

        answer = rag_chain_with_source.invoke(inquiry)
        return answer
    except Exception as e:
        print(e)
        raise e

def get_files_in_directory() -> list[str]:
    files = glob.glob(os.path.join('./documents', '*'))
    return [os.path.basename(file) for file in files if os.path.isfile(file)]

def get_closest_file_match(filename:str) -> str:
    files = get_files_in_directory()
    return difflib.get_close_matches(filename, files, cutoff=0, n=1)[0]