from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from vector_store import get_pinecone
import os

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def load_file(filepath: str):
    loader = UnstructuredFileLoader(filepath)
    docs = loader.load()
    for doc in docs:
        doc.metadata.update({'source': filepath})
    return docs

def load_directory(directory: str):
    loader = DirectoryLoader(directory)
    return loader.load()

def embed_docs(directory: str, embeddings: OpenAIEmbeddings):
    data = load_directory(directory)
    
    return embeddings.embed_documents(data)

def embed_doc(filepath:str, embeddings: OpenAIEmbeddings):
    data = load_file(filepath)
    return embeddings.embed_documents(data)

def upload_doc_to_pinecone(filepath:str):
    try:
        embeddings = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model="text-embedding-3-small")
        pinecone = get_pinecone(embeddings=embeddings)
        documents = load_file(filepath)
        pinecone.add_documents(documents)
        return "success"
    except Exception as e:
        raise e

def delete_file_from_pinecone(filepath:str):
    try:
        embeddings = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model="text-embedding-3-small")
        pinecone = get_pinecone(embeddings=embeddings)
        pinecone.delete(namespace=filepath)
        return "success"
    except Exception as e:
        raise e
