from fastapi import APIRouter, HTTPException
from models.request_bodies import ChatBody, UserSession
from utils.doc_manager import upload_doc_to_pinecone, delete_file_from_pinecone
from utils.test_agent import make_chain, format_conversation
from utils import azure
import openai
import os
client = openai.OpenAI()

ALLOWED_EXTENSIONS = {'txt', 'doc', 'sql', 'py', 'cs', 'docx', 'pdf'}

chatRouter =  APIRouter()
azureRouter=  APIRouter() 
pineconeRouter =  APIRouter()


chat_history = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@chatRouter.post("/generate")
def generate_chat(body: ChatBody):
    chain = make_chain(body.user_id, body.session_id)
    response = chain.invoke({"input" : body.message, "chat_history": chat_history})
    chat_history.append({"role": "assistant", "content": response['answer']})
    return {"data" : response['answer']}



@azureRouter.get("/repositories/{organization}/{project}")
def get_repositories(organization:str, project:str, 
                     skip:int | None = None, 
                     top:int | None = 100, 
                     fromDate:str | None = None, 
                     toDate:str | None = None, 
                     author:str | None = None, 
                     toCommitId:str | None = None, 
                     user:str | None = None):
    params = {
        '$skip': skip,
        '$top': top,
        'fromDate': fromDate,
        'toDate': toDate,
        'author': author,
        'toCommitId': toCommitId,
        'user': user
    }
    filtered_params = {k: v for k, v in params.items() if v is not None}
    return azure.request_repositories(organization, project, **filtered_params)

@azureRouter.get("/repositories/{organization}/{project}/{repository}/commits")
def get_commits(organization:str, project:str, repository:str, 
                skip:int | None = None, 
                top:int | None = 100, 
                fromDate:str | None = None, 
                toDate:str | None = None,):
    params = {
        '$skip': skip,
        '$top': top,
        'fromDate': fromDate,
        'toDate': toDate
    }
    filtered_params = {k: v for k, v in params.items() if v is not None}
    return azure.request_repository_commits(organization, project, repository, **filtered_params)

@azureRouter.post("/repositories/{organization}/{project}/{repository}/commits")
def post_commits(body: UserSession, organization:str, project:str, repository:str, 
                skip:int | None = None, 
                top:int = 100, 
                fromDate:str | None = None, 
                toDate:str | None = None,):
    params = {
        '$skip': skip,
        '$top': top,
        'fromDate': fromDate,
        'toDate': toDate
    }
    filtered_params = {k: v for k, v in params.items() if v is not None}
    json = azure.request_repository_commits(organization, project, repository, **filtered_params)
    return azure.ingest_commit_json(json, body.session_id, body.user_id)

@azureRouter.get("/repositories/{organization}/{project}/{repository}/fileStructure")
def get_file_structure(organization:str, project:str, repository:str,
                       directory:str | None = None,
                       file:str | None = None):
    try:
        response = azure.get_repository_overview(organization, project, repository)
        return response 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@azureRouter.get("/repositories/{organization}/{project}/{repository}/files")
def get_file(organization:str, project:str, repository:str, scopePath:str ):
    try:
        response = azure.get_file_path(organization, project, repository, scopePath)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

