import requests
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth
import dotenv
import os
import json
import re
from langchain_core.documents import Document
from database.vector_store import get_pinecone
dotenv.load_dotenv()
AZURE_PERSONAL_ACCESS_TOKEN = os.environ["AZURE_PERSONAL_ACCESS_TOKEN"]
AZURE_EMAIL = os.environ["AZURE_EMAIL"]
auth = HTTPBasicAuth(AZURE_EMAIL, AZURE_PERSONAL_ACCESS_TOKEN)

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


def request_repository_commits(organization: str, project: str, repository:str, **kwargs):
    # The kwargs are the elements of a repository that can be retrieved
    # acceptable kwargs are:
    # $skip - the numbe of commits to skip
    # $top - the number of commits you want to review (starting from the latest)
    # fromDate - the date you want to start from (6/14/2018 12:00:00 AM)
    # toDate - the date you want to end at (6/14/2018 12:00:00 AM)
    # author - the author of the commit
    # toCommitId - If provided, an upper bound for filtering commits alphabetically
    # user - the user who made the commit
    res = requests.get(
        url=f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository}/commits?includeWorkItems=True&includeUserImageUrl=False&includePushData=True",
        auth=auth,
        params=kwargs
    )
    return res.json()


def ingest_commit_json(data, session_id, user_id):
    # What to include in the langchain document per json object
    # author (name, email, date)
    # changeCounts
    # comment
    # commitId
    # committer
    # push (date, pushId)
    # workItems (id, url)
    # url
    # What to add as metadata:
    # author (name)
    # date
    # work item id(s)
    try:
        count = data['count']
        docs:Document = []
        for commit in data['value']:
            # Create a dictionary with the required key-value pairs
            document_content = {
                'author': {
                    'name': commit['author']['name'],
                    'email': commit['author']['email'],
                    'date': commit['author']['date']
                },
                'changeCounts': commit['changeCounts'],
                'comment': commit['comment'],
                'commitId': commit['commitId'],
                'push': {
                    'date': commit['push']['date'],
                    'pushId': commit['push']['pushId'],
                    'pushedBy' : commit['push']['pushedBy']['displayName']
                },
                'workItems': commit['workItems'],
                'url': commit['url']
            }
            document_content_str = json.dumps(document_content, indent=4)
            docs.append(Document(
                page_content=document_content_str,
                metadata={
                    'author': commit['author']['name'],
                    'date': commit['author']['date'],
                    'commitId' : commit['commitId'],
                    'workItemId': ','.join([item['id'] for item in commit['workItems']]),
                    'type' : 'azure-commits'
                }
            ))
        vector_store = get_pinecone(namespace=f"{user_id}_{session_id}")
        vector_store.add_documents(docs)
        return {"status" : "success", "count" : count}
    except Exception as e:
        return {"status" : "failed", "error" : str(e)}

def get_repository_items(organization: str, project: str, repository: str):
    return requests.get(
            url=f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository}/items?recursionLevel=full&api-version=7.1-preview.1",
            auth=auth
        ).json()

def get_repository_overview(organization: str, project: str, repository: str, directory: str = None):
    try:
          # Ensure the response is converted to JSON
        res = get_repository_items(organization, project, repository)
        file_structure = []
        folders = []
        # Initializing a mapping of folder paths to folder objects to easily append files to folders
        folder_mapping = {}

        for item in res['value']:
            if item['gitObjectType'] == 'tree' and item['isFolder']:
                # Create a folder structure
                folder = {
                    'id' : item['objectId'],
                    'url': item['url'],
                    'path': item['path'],
                    'type': 'directory',
                    'files': []
                }
                file_structure.append(folder)
                folders.append(item['path'])
                folder_mapping[item['path']] = folder
            elif item['gitObjectType'] == 'blob':
                # Create a file structure
                file = {
                    'id' : item['objectId'],
                    'url': item['url'],
                    'fileName': item['path'].split('/')[-1],
                    'fileType': item['path'].split('.')[-1] if '.' in item['path'] else '',
                    'path': item['path']
                }
                parent_path = '/'.join(item['path'].split('/')[:-1])
                if parent_path == "":
                    parent_path = "/"
                if parent_path in folder_mapping:
                    folder_mapping[parent_path]['files'].append(file)
                else:
                    file_structure.append(file)
        if directory:
            file_structure = [item for item in file_structure if item['path'].startswith(directory)]
            return {"status": "success", "folders":folders, "files" : file_structure}
        else:
            return {"status": "success", "folders":folders}
    except Exception as e:
        return HTTPException(500, detail=str(e))

def get_file_path(organization: str, project: str, repository: str, filename:str):
    data = get_repository_items(organization, project, repository)
    files = []
    for item in data['value']:
        pattern_with_extension = r'/[^/]*{}(?:\.\w+)?$'.format(re.escape(filename))
        pattern_without_extension = r'/[^/]*{}$'.format(re.escape(filename))
        if bool(re.search(pattern_with_extension, item['path'])) or bool(re.search(pattern_without_extension, item['path'])):
            files.append(item)
    return files

def make_file_text_req(organization, project, repository, scopePath):
    res = requests.get(
        url=f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository}/items?scopePath={scopePath}&api-version=7.1-preview.1",
        auth=auth
    )
    return res.content

def make_file_metadata_req(organization, project, repository, scopePath):
    res = requests.get(
        url=f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository}/items?path={scopePath}includeContentMetadata=True&api-version=7.1-preview.1",
        auth=auth
    )
    return res.json()

def get_file_metadata(organization: str, project: str, repository: str, scopePath:str):
    try:
        print(scopePath)
        res = make_file_metadata_req(organization, project, repository, scopePath)
        print(res)
        if (res['count'] == 0):
            updatedPaths = get_file_path(organization, project, repository, scopePath)
            reqs = []
            for updatedPath in updatedPaths:
                res = make_file_metadata_req(organization, project, repository, updatedPath['path'])
                if (res['count'] > 0):
                    reqs.append(res)
            if (res['count'] == 0):
                return HTTPException(404, detail="File not found")
            return reqs
        return res
    except Exception as e:
        return HTTPException(500, detail=str(e))