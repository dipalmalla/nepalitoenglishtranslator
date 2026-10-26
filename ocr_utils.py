import tempfile
import os
from typing import Optional
import pytesseract
from PIL import Image
import io
import pdf2image
import docx


def _configure_tesseract():
    tesseract_cmd = os.environ.get('TESSERACT_CMD')
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def _pdf_poppler_path():
    poppler = os.environ.get('POPPLER_PATH')
    if poppler and os.path.isdir(poppler):
        return poppler
    return None


_configure_tesseract()


def extract_text_from_file(data: bytes, filename: str) -> str:
    name = filename.lower()
    if name.endswith('.pdf'):
        return extract_text_from_pdf(data)
    if name.endswith('.docx'):
        return extract_text_from_docx(data)
    if name.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp')):
        return extract_text_from_image(data)
    raise ValueError('Unsupported file type. Please upload a PDF, DOCX, or image file (PNG/JPG/JPEG/BMP/TIFF).')


def extract_text_from_pdf(data: bytes) -> str:
    poppler_path = _pdf_poppler_path()
    try:
        images = pdf2image.convert_from_bytes(data, poppler_path=poppler_path) if poppler_path else pdf2image.convert_from_bytes(data)
    except Exception as exc:
        raise RuntimeError('PDF extraction failed. Please ensure Poppler is installed and added to PATH.') from exc
    parts = []
    for img in images:
        try:
            parts.append(pytesseract.image_to_string(img, lang='nep'))
        except Exception:
            try:
                parts.append(pytesseract.image_to_string(img))
            except Exception as exc:
                raise RuntimeError('OCR failed while processing the PDF. Please verify Tesseract is installed and configured.') from exc
    return '\n'.join(parts)


def extract_text_from_docx(data: bytes) -> str:
    bio = io.BytesIO(data)
    try:
        doc = docx.Document(bio)
    except Exception as exc:
        raise ValueError('The DOCX file could not be read.') from exc
    parts = []
    for p in doc.paragraphs:
        parts.append(p.text)
    return '\n'.join(parts)


def extract_text_from_image(data: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(data))
    except Exception as exc:
        raise ValueError('The uploaded image could not be opened.') from exc
    try:
        return pytesseract.image_to_string(img, lang='nep')
    except Exception:
        try:
            return pytesseract.image_to_string(img)
        except Exception as exc:
            raise RuntimeError('OCR failed while processing the image. Please verify Tesseract is installed and configured.') from exc
