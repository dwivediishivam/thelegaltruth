from flask import Flask, request, render_template
import os
import PyPDF2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'  # Ensure this directory exists or is created via your deployment setup

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and file.filename.endswith('.pdf'):
        # Simpler handling without os.path.join
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return process_pdf(filepath)
    return 'Invalid file type'

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
