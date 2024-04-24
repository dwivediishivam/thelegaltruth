from flask import Flask, request, render_template
import os
import PyPDF2

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('uploads')  # Using 'os.path.join' for future modifications
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the upload directory if it doesn't exist

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        return process_pdf(filepath)
    return 'Invalid file type', 400

def process_pdf(filepath):
    text = ""
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        num_pages = reader.numPages
        for page_number in range(num_pages):
            page = reader.getPage(page_number)
            text += page.extractText()
    return text

if __name__ == '__main__':
    app.run(debug=True)
