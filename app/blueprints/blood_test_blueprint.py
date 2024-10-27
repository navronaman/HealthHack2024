from flask import Blueprint, request, jsonify
from app.services.blood_test.s3_service import upload_to_s3
from app.services.blood_test.pdf_processing import extract_text_from_pdf
from app.services.blood_test.openai_service import analyze_text_with_openai
from app.services.blood_test.pdf_generator import create_pdf
import os

blood_test_blueprint = Blueprint('blood_test', __name__)

@blood_test_blueprint.route('/pdf-analysis', methods=['POST'])
def blood_test_analysis():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    local_pdf_path = "uploaded_report.pdf"
    file.save(local_pdf_path)
    
    pdf_text = extract_text_from_pdf(local_pdf_path)
    
    result_text = analyze_text_with_openai(pdf_text)
    
    if result_text is None:
        os.remove(local_pdf_path)
        return jsonify({"error": "Failed to analyze PDF content"}), 500
    
    output_pdf_path = "blood_test_report.pdf"
    create_pdf(result_text, output_pdf_path)
    
    s3_pdf_url = upload_to_s3(output_pdf_path, "blrood_test_report.pdf")
    
    os.remove(local_pdf_path)
    os.remove(output_pdf_path)
    
    if s3_pdf_url:
        return jsonify({"s3_url": s3_pdf_url})
    else:
        return jsonify({"error": "Failed to upload PDF to S3"}), 500
