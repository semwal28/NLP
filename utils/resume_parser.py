"""
Resume Parser Module.

Extracts plain text from uploaded PDF and DOCX resume files so that the
content can be sent to the Gemini API for analysis.
"""

from __future__ import annotations

import io
from typing import Optional

import PyPDF2
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Concatenated text from all pages of the PDF.
    """
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text content from a DOCX file.

    Args:
        file_bytes: Raw bytes of the uploaded DOCX file.

    Returns:
        Concatenated text from all paragraphs in the document.
    """
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs: list[str] = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text.strip())
    return "\n".join(paragraphs)


def parse_resume(file_bytes: bytes, file_name: str) -> Optional[str]:
    """Route the uploaded file to the appropriate text extractor.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        file_name: Original file name (used to determine file type).

    Returns:
        Extracted text, or ``None`` if the file type is unsupported.
    """
    lower_name = file_name.lower()
    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    return None
