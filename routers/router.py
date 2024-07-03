from fastapi import APIRouter, HTTPException, UploadFile
import shutil
from models.request_bodies import ChatBody, UserSession
from utils.retrieve_data import CodeAgent
from utils.doc_manager import upload_doc_to_pinecone, delete_file_from_pinecone
from utils.agents.test_agent import make_chain, format_conversation
from utils import azure
import openai
import os
client = openai.OpenAI()

ALLOWED_EXTENSIONS = {'txt', 'doc', 'sql', 'py', 'cs', 'docx', 'pdf'}

chatRouter =  APIRouter()
azureRouter=  APIRouter() 
fileRouter =  APIRouter()


chat_history = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

####################
# Chat With Agents #
####################
@chatRouter.post("/generate")
def generate_chat(body: ChatBody):
    chain = make_chain(body.user_id, body.session_id)
    response = chain.invoke({"input" : body.message, "chat_history": chat_history})
    chat_history.append({"role": "assistant", "content": response['answer']})
    return {"data" : response['answer']}

@chatRouter.post("/complex_generate")
def generate_chat(body:ChatBody):
    response = CodeAgent(body.user_id, body.session_id).start_chain(body.message)
    return response

####################
# File Management  #
####################
@fileRouter.post("/upload")
def upload_file(user_id:int, session_id:int, file:UploadFile):
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No file uploaded")
    if allowed_file(file.filename.split('.')[-1]):
        raise HTTPException(status_code=400, detail="File type not allowed")
    try:
        filepath = os.path.join(os.getcwd(), "documents", file.filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)
        docs = upload_doc_to_pinecone(filepath, user_id, session_id)
        return {"status": "success", "documents" : docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    




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

