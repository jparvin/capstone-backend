import os
from langchain_openai import OpenAIEmbeddings
from PineconeVectorStore import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
import requests
load_dotenv()

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

def get_pinecone(embeddings:OpenAIEmbeddings) -> PineconeVectorStore:
    # For some reason the SSL Certificate isn't getting passed when I try to run request commands, so I am just disabling it for now
    # To re-enable it just turn the ssl_verify to true
    pinecone = Pinecone(api_key=PINECONE_API_KEY, ssl_verify=False)
    return  PineconeVectorStore(
        client=pinecone,
        embedding=embeddings
    )