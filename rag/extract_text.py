import os
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # change path if different


def extract_text(file, filename):
    ext = os.path.splitext(filename)[-1].lower()
    if ext == '.pdf':
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == '.docx':
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == '.txt':
        return file.read().decode("utf-8")
    elif ext == '.csv':
        df = pd.read_csv(file)
        return df.to_string(index=False)
    elif ext in ['.png', '.jpg', '.jpeg']:
        try:
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise ValueError(f"Image OCR failed: {str(e)}")

    
    else:
        raise ValueError(f"Unsupported file type: {ext}")
