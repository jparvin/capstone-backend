import os
from langchain_aws import BedrockEmbeddings
from utils.agents.aws_setup import BedrockLLM
from .PineconeVectorStore import *
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

def get_pinecone():
    return Pinecone(api_key=PINECONE_API_KEY, ssl_verify=False)

def get_langchain_pinecone(namespace:str) -> PineconeVectorStore:
    # For some reason the SSL Certificate isn't getting passed when I try to run request commands, so I am just disabling it for now
    # To re-enable it just turn the ssl_verify to true
    embeddings = BedrockEmbeddings(
            client=BedrockLLM.get_bedrock_runtime_client(),
            model_id="amazon.titan-embed-g1-text-02"
            )
    
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