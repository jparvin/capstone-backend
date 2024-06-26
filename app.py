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

client = openai.OpenAI()
UPLOAD_FOLDER = 'documents'
ALLOWED_EXTENSIONS = {'txt', 'doc', 'sql', 'py', 'cs', 'docx'}

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

@app.route("/stream", methods=["GET"])
def stream():
    # You need to extract the user message and chat history from your data structure
    question = chat_history[-1]["content"]
    chain = make_chain(chat_history)
    response = chain.invoke({"input" : question, "chat_history": chat_history})
    print(response)
    def generate():
        try:
            print(response['answer'])
            yield f"data: {response['answer']}"
            
            # Once the loop is done, append the full message to chat_history
            chat_history.append({"role": "assistant", "content": response['answer']})
        except Exception as e:
            print(e)
            chat_history.append({"role": "system", "content": "An error occurred. Please try again."})
            yield f"data: An error occurred. Please try again.\n\n"
    
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/generate", methods=["GET"])
def generate():
    question = chat_history[-1]["content"]
    chain = make_chain(chat_history)
    response = chain.invoke({"input" : question, "chat_history": chat_history})
    chat_history.append({"role": "assistant", "content": response['answer']})
    return jsonify({"data" : response['answer']})




@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)