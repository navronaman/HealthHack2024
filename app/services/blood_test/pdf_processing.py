import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    What does this function do?
    - Extracts text from a PDF file
    - Returns the extracted text as a string
    Parameters:
    - pdf_path: The path to the PDF file
    Returns:
    - text: A string containing the extracted text from the PDF
    """
    
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text()
    return text

if __name__ == "__main__":
    pdf_path = r"app\templates\blood_test\sample_test.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)
    
    pdf_path2 = r"app\templates\blood_test\blood_test_report_output.pdf"
    extracted_text2 = extract_text_from_pdf(pdf_path2)
    print(extracted_text2)
