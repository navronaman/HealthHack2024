"""
What does this file used for?
The functions in this file are used to provide the backend services for the blood test analysis application.
extract_text_from_pdf: Extracts text from a PDF file.
upload_to_s3: Uploads a file to an AWS S3 bucket.
analyze_text_with_openai: Analyzes text using the OpenAI API.
create_pdf: Creates a PDF file with the given text.
"""

# For PDF Processing
import fitz  # PyMuPDF

# For S3 Service
import boto3
from botocore.exceptions import NoCredentialsError

# For S3 Services
import os
from dotenv import load_dotenv

# For OpenAI Service
import openai # Important: Version = 0.28.0

# For PDF Generator
from fpdf import FPDF

# Load environment variables
load_dotenv()

# AWS S3 credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION_NAME = os.getenv("S3_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt file path
BR_PROMPT_FILE_PATH = r"data\templates\blood_test\blood_test_prompt.txt" # Fill this out
UR_PROMPT_FILE_PATH = r"data\templates\urine_test\urine_test_prompt.txt" # Fill this out

# Let's start with the PDF processing service

def extract_text_from_pdf(pdf_path):
    """
    What does this function do?
    - Extracts text from a PDF file
    - Returns the extracted text as a string
    - Usecases: All possible PDF files
    
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

# Next, let's implement the S3 service

s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
)

def upload_to_s3(file_path, s3_filename):
    """
    Uploads a file to an S3 bucket.
    
    Parameters:
    - file_path (str): Local path to the file to be uploaded.
    - s3_filename (str): Destination path in the S3 bucket.
    - Depending on the test type, the destination path might be changed to blood_report, urine_report, MRI_report, etc.
    
    Returns:
    - str: S3 URL of the uploaded file if successful.
    - None: If an error occurs.
    """
    try:
        s3.upload_file(file_path, S3_BUCKET, s3_filename)
        
        # Generate a presigned URL for the file with a 1-hour expiration
        s3_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_filename},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        return s3_url
    except NoCredentialsError:
        print("Error: AWS credentials not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Third, let's implement the OpenAI service
def analyze_text_with_openai(input_text, test_type='Blood Type', prompt_file_path=BR_PROMPT_FILE_PATH):
    """
    Takes in the text from the blood test and uses OpenAI to analyze it, adds a prompt to give context.
    
    Parameters:
    - input_text (str): The text to be analyzed.
    - test_type (str): The type of test being analyzed. [Blood Test, Urine Test, MRI Scan, etc.]
    - prompt_file_path (str): The path to the prompt file. [Blood Test Prompt, Urine Test Prompt, MRI Scan Prompt, etc.]
    
    Returns:
    - result (str): The analyzed text from OpenAI.
    
    """
    with open(prompt_file_path, "r") as prompt_file:
        prompt_template = prompt_file.read()
    
    full_prompt = f"{prompt_template}\n\n{test_type} Findings:\n{input_text}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        result = response['choices'][0]['message']['content']
        return result
    except FileNotFoundError:
        print("Error: The specified prompt file was not found.")
        return None
    except KeyError:
        print("Error: Unexpected response format from OpenAI API.")
        return None
    except Exception as e:
        print("Error with OpenAI API:", e)
        return None

# Lastly, let's implement the PDF generation service
def create_pdf(output_text, pdf_filename=r"data\templates\report_output0.pdf"):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Patient Blood Test Analysis Report", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    sections = output_text.split("\n")
    for line in sections:
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            pdf.ln(10)
            pdf.set_font("Arial", "B", 12)
        elif line.startswith("-"):
            pdf.set_font("Arial", "I", 12)
            pdf.cell(10)
        
        pdf.multi_cell(0, 10, line)
    
    pdf.output(pdf_filename)
    return pdf_filename

if __name__ == '__main__':
    
    print("Unit Test #1 for Function #1 - Extract Text from PDF")
    
    pdf_path = r"data\templates\blood_test\sample_test.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)
    
    print("Unit Test #2 for Function #1 - Extract Text from PDF")
    pdf_path2 = r"data\templates\blood_test\blood_test_report_output.pdf"
    extracted_text2 = extract_text_from_pdf(pdf_path2)
    print(extracted_text2)
    
    print("Unit Test #1 for Function #2 - Upload to S3")
    url = upload_to_s3(pdf_path, "sample_test.pdf")
    print(url)
    
    print("Unit Test #1 for Function #3 - Analyze Text with OpenAI")
    test_text = """The patient's blood test results are as follows:
    1. Hemoglobin: 12.5 g/dL
    2. White Blood Cells: 8.2 x10^3/uL
    3. Platelets: 150 x10^3/uL
    - Hemoglobin levels are within normal range.
    - White blood cell count is slightly elevated.
    - Platelet count is normal."""
    
    result = analyze_text_with_openai(test_text)
    print(result)
    
    print("Unit Test #1 for Function #4 - Create PDF")

    create_pdf(test_text, pdf_filename=r"data\templates\blood_test\blood_test_report_output2.pdf")
    