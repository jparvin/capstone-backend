from flask import (
    Flask,
    redirect,
    render_template,
    request,
    Response,
    stream_with_context,
    jsonify,
    url_for,
    send_from_directory,
    current_app,
    g
)
import threading
from werkzeug.utils import secure_filename
import os
import openai
from doc_manager import upload_doc_to_pinecone, delete_file_from_pinecone
from test_agent import make_chain, format_conversation
from azure import request_repositories, request_repository_commits, ingest_commit_json

client = openai.OpenAI()
UPLOAD_FOLDER = 'documents'
ALLOWED_EXTENSIONS = {'txt', 'doc', 'sql', 'py', 'cs', 'docx', 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


chat_history = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=chat_history)

@app.route("/chat", methods=["POST"])
def chat():
    content = request.json["message"]
    chat_history.append({"role": "human", "content": content})
    return jsonify(success=True)

@app.route('/uploads', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            upload_doc_to_pinecone(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', filename=filename))
    return url_for('list_files')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route('/uploads')
def list_files():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("file_list.html", data=files)

@app.route('/delete/<filename>')
def delete_file(filename):
    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    delete_file_from_pinecone(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template("file_list.html", data=files)

@app.route("/delete")
def delete_files():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    for file in files:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], file))
        delete_file_from_pinecone(os.path.join(app.config['UPLOAD_FOLDER'], file))
    return jsonify(success=True)

@app.route("/generate", methods=["GET"])
def generate():
    question = chat_history[-1]["content"]
    chain = make_chain(1, 1)
    response = chain.invoke({"input" : question, "chat_history": chat_history})
    chat_history.append({"role": "assistant", "content": response['answer']})
    return jsonify({"data" : response['answer']})

@app.route("/<user_id>/<session_id>/generate", methods=["POST"])
def generate_chat(user_id:int, session_id: int):
    question = request.get_json()["message"]
    chain = make_chain(user_id, session_id)
    response = chain.invoke({"input" : question, "chat_history": chat_history})
    chat_history.append({"role": "assistant", "content": response['answer']})
    return jsonify({"data" : response['answer']})


@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    return jsonify(success=True)


@app.route("/repositories/<organization>/<project>", methods=["POST", "GET"])
def get_repositories(organization:str, project:str):
    if request.method == "GET":
        return request_repositories(organization, project, **request.args)
    if request.method == "POST":
        return

@app.route("/<user_id>/<session_id>/repositories/<organization>/<project>/<repository>/commits", methods=["GET", "POST"])
def get_repository_commits(user_id:int, session_id: int, organization:str, project:str, repository:str):
    if request.method == "GET":
        return request_repository_commits(organization, project, repository, **request.args)
    if request.method == "POST":
        json = request_repository_commits(organization, project, repository, **request.args)
        return ingest_commit_json(json, session_id, user_id)

if __name__ == '__main__':
    app.run(debug=True)