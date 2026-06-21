import PyPDF2
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    return text.strip()

if __name__ == "__main__":
    # Test
    path = "CV_ManuelNavas_Especialista_IT.pdf"
    if os.path.exists(path):
        cv_text = extract_text_from_pdf(path)
        print(f"Extracted {len(cv_text)} characters from CV.")
