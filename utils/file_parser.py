import io

from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = ["txt", "pdf", "docx"]


def extract_txt(file):
    """Extract text from a TXT file."""

    raw_data = file.getvalue()

    try:
        return raw_data.decode("utf-8")
    except UnicodeDecodeError:
        return raw_data.decode("latin-1")


def extract_pdf(file):
    """Extract text from a PDF file."""

    pdf_bytes = io.BytesIO(file.getvalue())
    reader = PdfReader(pdf_bytes)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(pages)


def extract_docx(file):
    """Extract text from a DOCX file."""

    docx_bytes = io.BytesIO(file.getvalue())
    document = Document(docx_bytes)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def extract_text(file):
    """
    Extract text from TXT, PDF or DOCX files.
    """

    if file is None:
        return ""

    file_name = file.name.lower()

    if file_name.endswith(".txt"):
        return extract_txt(file)

    elif file_name.endswith(".pdf"):
        return extract_pdf(file)

    elif file_name.endswith(".docx"):
        return extract_docx(file)

    else:
        raise ValueError(
            "Unsupported file type. Please upload a TXT, PDF or DOCX file."
        )