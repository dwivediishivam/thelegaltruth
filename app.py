from flask import Flask, request, render_template, session
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = 'allo'

UPLOAD_FOLDER = os.path.join('uploads')  # Using 'os.path.join' for future modifications
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the upload directory if it doesn't exist

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        session['filepath'] = filepath
        return process_pdf(filepath)
    return 'Invalid file type', 400

def process_pdf(filepath):
    # Create an assistant
    assistant = client.beta.assistants.create(
        name="Legal Documents Analyser and Support Assistant (LegalEase)",
        instructions="You are an expert legal analyst. Use your knowledge base to answer questions about the given legal statements. Remember for all instances, no need to give any references. just return plain text.",
        model="gpt-4-turbo",
        tools=[{"type": "file_search"}],
    )

    vector_store = client.beta.vector_stores.create(name="Legal Documents")
    # Ready the files for upload to OpenAI
    file_paths = [filepath]
    file_streams = [open(path, "rb") for path in file_paths]

    # Upload the files, add them to the vector store, and poll the status of the file batch
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    # Update the assistant with the vector store
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    # Upload the user-provided file to OpenAI
    message_file = client.files.create(file=open(filepath, "rb"), purpose="assistants")

    session['assistant_id'] = assistant.id
    session['message_file_id'] = message_file.id

    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Read the document that has been provided to you in your knowledge carefully and then give me a summary of the same.",
                "attachments": [{"file_id": message_file.id, "tools": [{"type": "file_search"}]}],
            }
        ]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    message_content = messages[0].content[0].text
    return str(message_content.value)

@app.route('/chat', methods=['POST'])
def chat():

    filepath = session['filepath']
    assistant_id = session['assistant_id']
    message_file_id = session['message_file_id']


    user_query = request.json.get('query')
    if not user_query:
        return ({'answer': 'No question provided'}), 400

    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Read the document that has been provided to you in your knowledge carefully that is the legal document on basis of which questions are being asked, so read that before you answer this or continue the conversation from before " + user_query,
                "attachments": [{"file_id": message_file_id, "tools": [{"type": "file_search"}]}],
            }
        ]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant_id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    response_text = [msg.content[0].text.value for msg in messages if msg.role == "assistant"]
    
    return {"answer": "\n".join(response_text)}, 200

if __name__ == '__main__':
    app.run(debug=True)