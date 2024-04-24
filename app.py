from flask import Flask, request, render_template
import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('uploads')  # Using 'os.path.join' for future modifications
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the upload directory if it doesn't exist

def read_pdf_contents(pdf_path):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        
        text = ''
        # Iterate through each page of the PDF
        for page_number in range(len(pdf_document)):
            # Extract text from the page
            page = pdf_document.load_page(page_number)
            text += page.get_text()
        
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def ocr_pdf_contents(pdf_path):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        
        text = ''
        # Iterate through each page of the PDF
        for page_number in range(len(pdf_document)):
            # Extract image from the page
            page = pdf_document.load_page(page_number)
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Perform OCR using Tesseract
            extracted_text = pytesseract.image_to_string(image)
            text += extracted_text
        
        return text
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return None
    
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

def process_pdf(pdf_path):
    pdf_text = read_pdf_contents(pdf_path)
    if pdf_text:
        return(pdf_text)

    ocr_text = ocr_pdf_contents(pdf_path)
    if ocr_text:
        return(ocr_text)








if __name__ == '__main__':
    app.run(debug=True)
