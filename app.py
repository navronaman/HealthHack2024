# Imports from Flask
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

# For client secret
import secrets

# For secrets
import os
from dotenv import load_dotenv

# Import from Backend
from backend.blood_service import extract_text_from_pdf, upload_to_s3, analyze_text_with_openai, create_pdf

# For session ID
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
CORS(app)

# Load environment variables
load_dotenv()

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# AWS S3 credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_REGION = os.getenv("S3_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

@app.route('/pdf-analysis', methods=['POST'])
def blood_test_analysis_pdf():
    """
    This is how the sample CURL request looks like:
    curl -X POST -F "file=@blood_test_report.pdf" http://localhost:5000/pdf-analysis
    
    This function does the following:
    - Receives a PDF file from the client
    - Stores the PDF file in the S3 bucket
    - Extracts text from the PDF file
    - Analyzes the extracted text using OpenAI
    - The analyzed text is then used to generate a report in form of a markdown text
    - We will store the report in a PDF file to the S3 bucket
    - Returns a JSON response with the analyzed text and the PDF report for the report
    
    Returns:
    - JSON response with the S3 URLs for the input and output PDFs, extracted text, and analyzed text
    {
        "input_pdf_url": "S3 URL for the input PDF",
        "output_pdf_url": "S3 URL for the output PDF",
        "extracted_text": "Extracted text from the input PDF",
        "gpt_analysis_text": "Analyzed text from the GPT model"
    }
    """
    # Check if a file is part of the request
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    # Generate a unique session identifier
    session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Define file paths and S3 paths
    input_s3_filename = f"input/{session_id}_{file.filename}"
    local_input_path = f"temp_input_{session_id}.pdf"
    file.save(local_input_path)  # Save temporarily before uploading
    
    # Upload the original PDF to S3 (input folder)
    input_s3_url = upload_to_s3(local_input_path, input_s3_filename)
    
    # Extract text from the uploaded PDF
    pdf_text = extract_text_from_pdf(local_input_path)
    
    # Analyze text with OpenAI API
    result_text = analyze_text_with_openai(pdf_text)
    
    if result_text is None:
        os.remove(local_input_path)
        return jsonify({"error": "Failed to analyze PDF content"}), 500
    
    # Generate the output PDF report from GPT-processed text
    output_pdf_filename = f"temp_output_{session_id}.pdf"
    create_pdf(result_text, output_pdf_filename)
    
    # Define output S3 path and upload generated PDF to S3 (output folder)
    output_s3_filename = f"output/{session_id}_report.pdf"
    output_s3_url = upload_to_s3(output_pdf_filename, output_s3_filename)
    
    # Remove temporary local files
    os.remove(local_input_path)
    os.remove(output_pdf_filename)
    
    # Return JSON response with S3 URLs for both input and output PDFs, along with extracted text
    return jsonify({
        "input_pdf_url": input_s3_url,
        "output_pdf_url": output_s3_url,
        "extracted_text": pdf_text,
        "gpt_analysis_text": result_text
    })
    
if __name__ == '__main__':
    app.run(debug=True)