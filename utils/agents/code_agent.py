from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, Runnable
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from ...database.vector_store import get_langchain_pinecone

def query_code(filename:str, inquiry:str, model:ChatOpenAI, user_id:int, session_id:int):
    try:
        PROMPT = """
        You are a code developer that is an expert in {coding_language}. 
        You will be provided with a given code file, and a question about the file and be expected to answer the questoin.


        Anything between the following `context`  html blocks is retrieved from a knowledge bank, not part of the conversation with the user
        <context>
            {context} 
        <context/>

        Question: {question}
        
        """
        pinecone:PineconeVectorStore = get_langchain_pinecone(namespace=f"{user_id}_{session_id}")
        retriever = pinecone.as_retriever(
            search_kwargs={'filter': {'source':filename}}
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
            {"context": retriever, "coding_language":filename.split('.')[1] ,"question": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)

        answer = rag_chain_with_source.invoke(inquiry)
        return answer
    except Exception as e:
        print(e)
        raise e
