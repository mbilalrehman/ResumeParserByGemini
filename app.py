import os
import json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from pypdf import PdfReader
from docx import Document
from resumeparser_aws import ats_extractor


app = Flask(__name__)


UPLOAD_PATH = os.path.join(os.getcwd(), "uploads")  
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)

# Home Route (Ab data=None bhejta hai)
@app.route('/')
def index():
    return render_template('index.html', data=None)

# Resume Processing Route
@app.route("/process", methods=["POST"])
def ats():
    # Session check ki zaroorat nahi
    
    if 'pdf_doc' not in request.files:
        return "No file uploaded!"
    
    doc = request.files['pdf_doc']
    if doc.filename == "":
        return "No selected file!"
    
    file_ext = doc.filename.split('.')[-1].lower()
    if file_ext not in ['pdf', 'docx']:
        return "Invalid file format. Please upload a PDF or Word document."
    
    doc_path = os.path.join(UPLOAD_PATH, f"file.{file_ext}")
    try:
        doc.save(doc_path)  
    except Exception as e:
        return f"Error saving file: {str(e)}"
    
    resume_text = _read_file_from_path(doc_path, file_ext)
    
    if "Error:" in resume_text:
        return render_template('index.html', data=None, error=resume_text)
        
    extracted_data = ats_extractor(resume_text)

    if "error" in extracted_data:
        error_msg = f"AI Parsing Error: {extracted_data.get('error')}. Raw: {extracted_data.get('raw_response', '')}"
        return render_template('index.html', data=None, error=error_msg)

    # Data ko wapis ussi template par bhej dein
    return render_template('index.html', data=extracted_data)

# Helper Function (Same as before)
def _read_file_from_path(path, file_ext):
    text = ""
    if os.path.exists(path):
        if file_ext == "pdf":
            reader = PdfReader(path)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif file_ext == "docx":
            doc = Document(path)
            text = " ".join([para.text for para in doc.paragraphs])
    else:
        return "Error: File not found!"
    
    return text

# Naya "Fake" Save Route (Aapki request k mutabiq)
@app.route('/save_fake', methods=['POST'])
def save_fake():
    # Yeh route data le ga, lekin kuch karega nahi
    # data = request.json 
    # print("Data received, but not saving (as requested).")
    return jsonify({'message': 'Data simulated as saved successfully!'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
