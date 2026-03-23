# extractor.py
import os
import PyPDF2
import csv
import json
from PIL import Image
import docx
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Extractor:
    def __init__(self):
        pass

    def ocr_image_extractor(self, file_path):
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='eng+vie')
        return text or "Không phát hiện được văn bản từ ảnh"

    def ocr_pdf_extractor(self, file_path):
        try:
            images = convert_from_path(file_path)
            text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image, lang='eng+vie')
                text += f"--- Trang {i+1} ---\n" + page_text + "\n"
            return text or "Không phát hiện văn bản trong PDF scan"
        except Exception as e:
            return f"Lỗi OCR PDF: {str(e)}"

    def text_extractor(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def pdf_extractor(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted
            if text.strip():
                return text
            else:
                return self.ocr_pdf_extractor(file_path)
        except Exception as e:
            return f"Lỗi khi đọc file PDF: {str(e)}"

    def word_extractor(self, file_path):
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    def csv_extractor(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            text = ""
            for row in reader:
                text += ', '.join(row) + "\n"
            return text

    def json_extractor(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=4)

    @staticmethod
    def truncate_text(text, max_length=10000):
        return text if len(text) <= max_length else text[:max_length] + "\n... (truncated)"

    def get_extractor_by_extension(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.txt':
            return self.text_extractor
        elif ext == '.pdf':
            return self.pdf_extractor
        elif ext == '.docx':
            return self.word_extractor
        elif ext == '.csv':
            return self.csv_extractor
        elif ext == '.json':
            return self.json_extractor
        elif ext in ['.png', '.jpg', '.jpeg']:
            return self.ocr_image_extractor
        else:
            return None
