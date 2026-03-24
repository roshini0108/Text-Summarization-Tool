"""
FastAPI backend for the Text Summarization Tool.
"""

import time
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from summarizer import compare_summaries_with_timing, summarize_text


app = FastAPI(title="Text Summarization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    method: str
    summary_length: str


class CompareRequest(BaseModel):
    text: str = Field(..., min_length=1)
    summary_length: str


def map_method_to_cli_choice(method: str) -> str:
    """
    Convert API method names into the existing CLI method choices.
    """
    method_map = {
        "transformer": "1",
        "nltk": "2",
    }
    return method_map.get(method.lower(), "")


def extract_text_from_txt(content: bytes) -> str:
    """
    Extract text from a plain text file.
    """
    try:
        return content.decode("utf-8").strip()
    except UnicodeDecodeError as error:
        raise HTTPException(status_code=400, detail="Unable to decode the text file as UTF-8.") from error


def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract text from a PDF file using PyPDF2.
    """
    try:
        from PyPDF2 import PdfReader
    except ImportError as error:
        raise HTTPException(status_code=500, detail="PyPDF2 is not installed.") from error

    try:
        reader = PdfReader(BytesIO(content))
        extracted_pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(extracted_pages).strip()
    except Exception as error:
        raise HTTPException(status_code=400, detail="Failed to extract text from the PDF file.") from error


def extract_text_from_docx(content: bytes) -> str:
    """
    Extract text from a DOCX file using python-docx.
    """
    try:
        from docx import Document
    except ImportError as error:
        raise HTTPException(status_code=500, detail="python-docx is not installed.") from error

    try:
        document = Document(BytesIO(content))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception as error:
        raise HTTPException(status_code=400, detail="Failed to extract text from the DOCX file.") from error


def extract_text_from_upload(filename: str, content: bytes) -> str:
    """
    Route uploaded files to the correct extraction logic.
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".txt":
        return extract_text_from_txt(content)
    if suffix == ".pdf":
        return extract_text_from_pdf(content)
    if suffix == ".docx":
        return extract_text_from_docx(content)

    raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a .txt, .pdf, or .docx file.")


@app.get("/")
def read_root():
    return {"message": "Text Summarization API is running."}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploaded.")

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    extracted_text = extract_text_from_upload(file.filename, content)

    if not extracted_text:
        raise HTTPException(status_code=400, detail="No readable text could be extracted from the file.")

    return {"text": extracted_text}


@app.post("/summarize")
def summarize(request: SummarizeRequest):
    cleaned_text = request.text.strip()
    method = map_method_to_cli_choice(request.method)

    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    if method not in {"1", "2"}:
        raise HTTPException(status_code=400, detail="Method must be 'transformer' or 'nltk'.")

    if request.summary_length not in {"short", "medium", "long"}:
        raise HTTPException(status_code=400, detail="Invalid summary length.")

    try:
        start_time = time.perf_counter()
        summary = summarize_text(cleaned_text, method, request.summary_length)
        elapsed_time = time.perf_counter() - start_time

        return {
            "summary": summary,
            "time": round(elapsed_time, 4),
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unable to generate summary: {error}") from error


@app.post("/compare")
def compare(request: CompareRequest):
    cleaned_text = request.text.strip()

    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    if request.summary_length not in {"short", "medium", "long"}:
        raise HTTPException(status_code=400, detail="Invalid summary length.")

    try:
        result = compare_summaries_with_timing(cleaned_text, request.summary_length)
        return {
            "transformer": result["transformer"],
            "nltk": result["nltk"],
            "transformer_time": round(result["transformer_time"], 4),
            "nltk_time": round(result["nltk_time"], 4),
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unable to compare summaries: {error}") from error
