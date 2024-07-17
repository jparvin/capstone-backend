from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from database.vector_store import get_langchain_pinecone, get_pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

def get_splitter(separators = ["\n\n", "\n", ".", " "], chunk_size = 1000, chunk_overlap = 50):
    return RecursiveCharacterTextSplitter(
        separators=separators,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

def load_documentation_file(filepath: str, category:str):
    loader_docs = UnstructuredFileLoader(filepath).load()
    for doc in loader_docs:
        doc.metadata = {'source': os.path.basename(filepath), 'type': category}
    docs = get_splitter().split_documents(loader_docs)
    return docs

def load_directory(directory: str):
    loader = DirectoryLoader(directory)
    return loader.load()

def embed_docs(directory: str, embeddings: OpenAIEmbeddings):
    data = load_directory(directory)
    
    return embeddings.embed_documents(data)

def embed_doc(filepath:str, embeddings: OpenAIEmbeddings):
    data = load_documentation_file(filepath)
    return embeddings.embed_documents(data)

def upload_doc_to_pinecone(filepath:str, user_id:int, session_id:int, category:str):
    try:
        pinecone:PineconeVectorStore = get_langchain_pinecone(namespace=f"{user_id}_{session_id}")
        documents = load_documentation_file(filepath, category)
        print(documents)
        docs = pinecone.add_documents(documents)
        print(docs)
        return documents
    except Exception as e:
        raise e

def delete_file_from_pinecone(file:str, user_id:int, session_id:int):
    try:
        pinecone = get_pinecone()
        index = pinecone.Index(PINECONE_INDEX_NAME)
        docs = index.query(
                        vector=[item for item in [0.1] for _ in range(1536)],
                        namespace=f"{user_id}_{session_id}",
                        filter={"source": file},
                        top_k=1000,
                        include_metadata=True,
                    )
        ids = []
        for vector in docs["matches"]:
            ids.append(vector["id"])
        print(ids)
        print(ids.__len__())
        print(docs)
        
        if ids.__len__() != 0:
            index.delete(
                namespace=f"{user_id}_{session_id}",
                ids=ids,
            )
        return "success"
    except Exception as e:
        raise e
