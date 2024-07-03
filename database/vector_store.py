import os
from langchain_openai import OpenAIEmbeddings
from .PineconeVectorStore import *
from pinecone import Pinecone
from dotenv import load_dotenv
import requests
load_dotenv()

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def get_pinecone():
    return Pinecone(api_key=PINECONE_API_KEY, ssl_verify=False)

def get_langchain_pinecone(namespace:str) -> PineconeVectorStore:
    # For some reason the SSL Certificate isn't getting passed when I try to run request commands, so I am just disabling it for now
    # To re-enable it just turn the ssl_verify to true
    embeddings = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model="text-embedding-3-small")
    
    return  PineconeVectorStore(
        client=get_pinecone(),
        embedding=embeddings,
        index_name=PINECONE_INDEX_NAME,
        namespace=namespace
    )

def get_pinecone_metadata(namespace:str, **kwargs):
    pc = get_pinecone()
    index = pc.Index(PINECONE_INDEX_NAME)
    filter = {}
    for k, v in kwargs.items():
        filter
    index.query(namespace, filter={

    })