import os
import boto3
import langchain
import os
from langchain_community.llms.bedrock import BedrockBase
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
load_dotenv()
MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
TEMPERATURE = 0.5
AWS_ACCESS_KEY_ID = os.environ["aws_access_key_id"]
AWS_SECRET_ACCESS_KEY = os.environ["aws_secret_access_key"]
AWS_SESSION_TOKEN = os.environ["aws_session_token"]
AWS_REGION = os.environ["AWS_REGION"]

class BedrockLLM:

    @staticmethod
    def get_bedrock_client():
        """ 
        This function will return bedrock client.
        """
        bedrock_client = boto3.client(
            'bedrock',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN
            
        )

        return bedrock_client


    @staticmethod
    def get_bedrock_runtime_client():
      
        """ 
        This function will return bedrock runtime client.
        """
        bedrock_runtime_client = boto3.client(
            'bedrock-runtime',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN
        )

        return bedrock_runtime_client

    @staticmethod
    def get_bedrock_llm(
          model_id:str = MODEL,
          temperature:float = TEMPERATURE,
        ) -> BedrockBase:
        """
        This function will take multiple arguments and give
        
        input args: model_id, and temprature.

        output: return bedrock llm
        """
        params = {
            "temperature": temperature,
            "max_tokens_to_sample": 4096
        }

        bedrock_llm = BedrockBase(
            model_id=model_id,
            client=BedrockLLM.get_bedrock_runtime_client(),
            model_kwargs=params,
        )

        return bedrock_llm
    
    @staticmethod
    def get_bedrock_chat(
        model_id:str = MODEL,
        temperature:float = TEMPERATURE,
    ):
        """
        This function will take multiple arguments and give
        
        input args: model_id, and temprature.

        output: return bedrock chat
        """

        bedrock_chat = ChatBedrockConverse(
            model_id=model_id,
            client=BedrockLLM.get_bedrock_runtime_client(),
            temperature=temperature,
            max_tokens=4096
        )

        return bedrock_chat