import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
load_dotenv()

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

def get_pinecone(embeddings:OpenAIEmbeddings) -> PineconeVectorStore:
    return PineconeVectorStore(
        pinecone_api_key=PINECONE_API_KEY,
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings
    )