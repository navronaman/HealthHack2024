from fpdf import FPDF

def create_pdf(output_text, pdf_filename="blood_test_report_output.pdf"):
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

if __name__ == "__main__":
    output_text = """1. Hemoglobin: 12.5 g/dL
    2. White Blood Cells: 8.2 x10^3/uL
    3. Platelets: 150 x10^3/uL
    - Hemoglobin levels are within normal range.
    - White blood cell count is slightly elevated.
    - Platelet count is normal."""
    
    create_pdf(output_text, pdf_filename=r"app\templates\blood_test\blood_test_report_output2.pdf")