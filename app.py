import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
from flask import Flask, request, render_template
import os
import openai

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('uploads')  # Using 'os.path.join' for future modifications
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the upload directory if it doesn't exist

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

openai.api_key = os.getenv('OPENAI_API_KEY')

def pdf_to_ocr_text(filepath):
    doc = fitz.open(filepath)
    text = ''

    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        page_text = pytesseract.image_to_string(img)
        text += page_text

    return text

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
    # Perform OCR on the PDF
    extracted_text = pdf_to_ocr_text(filepath)
    return f'OCR Extracted Text: {extracted_text}'

if __name__ == '__main__':
    app.run(debug=True)
