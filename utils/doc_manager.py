from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from database.vector_store import get_langchain_pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
def get_splitter(separators = ["\n\n", "\n", ".", " "], chunk_size = 1000, chunk_overlap = 50):
    return RecursiveCharacterTextSplitter(
        separators=separators,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

def load_documentation_file(filepath: str):
    loader_docs = UnstructuredFileLoader(filepath).load()
    for doc in loader_docs:
        doc.metadata = {'source': os.path.basename(filepath), 'type': 'documentation'}
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

def upload_doc_to_pinecone(filepath:str):
    try:
        pinecone:PineconeVectorStore = get_langchain_pinecone(namespace="docs")
        documents = load_documentation_file(filepath)
        pinecone.add_documents(documents)
        return documents
    except Exception as e:
        raise e

def delete_file_from_pinecone(filepath:str):
    try:
        pinecone = get_langchain_pinecone(namespace="docs")
        pinecone.delete(namespace=filepath)
        return "success"
    except Exception as e:
        raise e
