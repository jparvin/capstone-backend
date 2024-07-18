from langchain_aws import ChatBedrock
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, Runnable
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from database.vector_store import get_langchain_pinecone

def query_documentation(files:list[str], inquiry:str, model:ChatBedrock, user_id:int, session_id:int):
    try:
        PROMPT = """
        You are a code developer that is an expert in documentation and translation of business requests to code.
        You will be provided with documentation about a given topic, and will need to answer questions about it.


        Anything between the following `context`  html blocks is retrieved from a knowledge bank, not part of the conversation with the user
        <context>
            {context} 
        <context/>

        Question: {question}
        
        """
        pinecone:PineconeVectorStore = get_langchain_pinecone(namespace=f"{user_id}_{session_id}")
        if files is None or files.__len__() == 0:
            retriever = pinecone.as_retriever(
                search_kwargs={'filter': {'source':{"$in":files}}}
            )
        else:
            retriever = pinecone.as_retriever(
                search_kwargs={'filter': {'type': "documentation"}}
            )

        custom_rag_prompt = PromptTemplate.from_template(PROMPT)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
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
    
def retrieve_docs(files: list[str], inquiry:str, user_id:int, session_id:int):
    pinecone:PineconeVectorStore = get_langchain_pinecone(namespace=f"{user_id}_{session_id}")
    if files is None or files.__len__() == 0:
        docs = pinecone.similarity_search(
            filter={"type": "documentation"}, query=inquiry
        )
    else:
        docs = pinecone.similarity_search(
            filter={"source": {"$in": files}}, query=inquiry
        )
    return docs