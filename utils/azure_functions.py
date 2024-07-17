import requests
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth
import dotenv
import os
import json
import re
from models.db_models import User, SessionModel
from langchain_core.documents import Document
from database.vector_store import get_pinecone
dotenv.load_dotenv()
from sqlalchemy.orm import Session
AZURE_PERSONAL_ACCESS_TOKEN = os.environ["AZURE_PERSONAL_ACCESS_TOKEN"]
AZURE_EMAIL = os.environ["AZURE_EMAIL"]
auth = HTTPBasicAuth(AZURE_EMAIL, AZURE_PERSONAL_ACCESS_TOKEN)

def get_auth(user_id:int, db:Session):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return HTTPBasicAuth(user.email, user.azure_personal_access_token)


def retrieve_file_structure(user_id: int, session_id:int, db: Session):
    auth = get_auth(user_id, db)
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    res = requests.get(
        url=f"https://dev.azure.com/{session.organization}/{session.project}/_apis/git/repositories/{session.repository}/items?api-version=7.1-preview.1",
        auth=auth
    )
    return res.json()

def format_json(json):
    formatted_json = {
        "count" : json['count'],
        "branches" : []
    }
    for item in json['value']:
        formatted_json['branches'].append({
            "name" : item['name'],
            "url" : item['url'],
            "webUrl" : item['webUrl'],
            "defaultBranch" : item['defaultBranch'],
            "id" : item['id']
        })
    return formatted_json

def request_repositories(organization: str, project: str, **kwargs):    
    if not kwargs:
        res = requests.get(
            url=f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories?api-version=7.1-preview.1",
            auth=auth
        )
        return format_json(res.json())
    
    repository = kwargs.get('repository')
    if repository is not None:
        res = requests.get(
            url=f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository}?api-version=7.1-preview.1",
            auth=auth
        )
        item = res.json()
        return {
            "name": item['name'],
            "url": item['url'],
            "webUrl": item['webUrl'],
            "defaultBranch": item['defaultBranch'],
            "id": item['id'],
            "links": item['_links']
        }
    
    return {"error": "enter a valid repository name as 'repository' parameter."}