import io
import re
import pymupdf
import docx
from fastapi import HTTPException

def clean_text(text: str) -> str:
    """
    Clean extracted text:
    - remove unnecessary whitespace
    - normalize line breaks
    - preserve paragraph boundaries
    """
    # Normalize multiple newlines to double newline (paragraph boundary)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text

def extract_text_from_pdf(content: bytes) -> str:
    try:
        doc = pymupdf.open(stream=content, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        return clean_text("".join(text_parts))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_docx(content: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(content))
        text_parts = [para.text for para in doc.paragraphs]
        return clean_text("\n".join(text_parts))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from DOCX: {str(e)}")

def extract_text_from_txt(content: bytes) -> str:
    try:
        # Try decoding with utf-8, fallback to latin-1
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin-1')
        return clean_text(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from TXT: {str(e)}")

def extract_text(content: bytes, filename: str, content_type: str) -> str:
    if not content:
        raise HTTPException(status_code=400, detail="Document is empty")

    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(content)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or filename.lower().endswith(".docx"):
        return extract_text_from_docx(content)
    elif content_type == "text/plain" or filename.lower().endswith(".txt"):
        return extract_text_from_txt(content)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type for {filename}")
