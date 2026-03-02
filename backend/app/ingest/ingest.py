# 1. Document loading
#     Reads files (PDF, DOCX, HTML, etc.).
#     uses pdfplumber (regular PDFs) and pdf2image + pytesseract (scanned PDFs).
# 2. Text extraction
#     Pulls out the raw text from pages.
#     Example: get "Introduction: This is a research paper...".
# 3. Preprocessing / NLP cleanup
#     Removes weird spacing, symbols, stopwords.
#     Uses spaCy for:
#         Sentence segmentation → splitting long text into sentences.
#         Tokenization, lemmatization (optional).
#         Named Entity Recognition (optional if you want metadata like dates/people).
# 4. Chunking
#     Breaks text into chunks of ~300–500 words with some overlap.
#     Why? Because LLMs work better with bite-sized context than huge documents.

from docx import Document as DocxDocument
import re
import requests
from bs4 import BeautifulSoup
import unicodedata
import logging
import os
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
# import fitz
import spacy

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHUNK_DEBUG_DIR = os.path.join(DATA_DIR, "chunk_debug")

os.makedirs(CHUNK_DEBUG_DIR, exist_ok=True)

# integrate pdf2image + pytesseract later for scanned PDFs

try:
    # only does tokenisation + sentence segmentation
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    logger.info("spaCy model 'en' loaded successfully.")
except OSError as e:
    logger.warning(f"Failed to load spaCy model: {e}")
    logger.info("Please make sure spaCy is installed and models are available.")

# def pdf_to_text(file):
# # using pymupdf instead (fitz) instead of pdf plumber
#     logger.info(f"Starting text extraction from PDF: {file}")

#     text = ""

#     try:
#         if hasattr(file, "read"):
#             # file-like object (SpooledTemporaryFile, UploadFile.file, etc.)
#             file.seek(0)
#             pdf_bytes = file.read()
#             doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#         else:
#             # path-like
#             doc = fitz.open(file)

#     except Exception as e:
#         logger.error(f"Failed to open PDF: {e}")
#         return ""

#     page_count = len(doc)

#     for page in doc:
#         # "text" mode preserves line breaks as seen visually
#         page_text = page.get_text("text")
#         if page_text:
#             text += page_text + "\n"
#         else:
#             logger.warning(f"No extractable text found on page {page.number + 1}")

#     # 1. Repair hyphenated words split by line breaks
#     text = re.sub(r"(\w)-\s*\n(\w)", r"\1\2", text)

#     # 2. Normalize whitespace (replace multiple spaces/tabs with one space)
#     text = re.sub(r"[ \t]+", " ", text)

#     # 3. Standardize paragraph breaks (max two newlines)
#     text = re.sub(r"\n\s*\n+", "\n\n", text)

#     # Strip leading/trailing spaces
#     text = text.strip()

#     logger.info(f"Extracted text from {page_count} pages ({len(text)} characters total).")
#     return text

# using pdf plumber
def pdf_to_text(file):
    logger.info(f"Starting text extraction from PDF")   

    text = ""

    page_count = 0

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_count += 1
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                logger.warning(f"No extractable text found on page {page.page_number}")
    
    # 2. Repair hyphenated words split by line breaks
    text = re.sub(r"(\w)-\s*\n(\w)", r"\1\2", text)
    
    # 3. Normalize whitespace (Replace multiple spaces/tabs with one space)
    text = re.sub(r"[ \t]+", " ", text)
    
    # 4. Standardize paragraph breaks (Max two newlines)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    
    text = text.strip()

    logger.info(f"Extracted text from {page_count} pages ({len(text)} characters total).")
    return text

def scanned_pdf_to_text(file):
    logger.info("Using OCR for scanned PDF")
    file.seek(0)
    images = convert_from_bytes(file.read())
    text = ""
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image)
        if page_text.strip():
            text += page_text + "\n"
        else:
            logger.warning(f"No text found on page {i+1}")
    return text.strip()

def extract_pdf_text(file):
    text = pdf_to_text(file)
    if len(text.strip()) < 100:
        logger.info("Low text yield — switching to OCR")
        file.seek(0)
        text = scanned_pdf_to_text(file)
    return text

def docx_to_text(file):
    logger.info("Extracting text from DOCX")
    doc = DocxDocument(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def url_to_text(url: str):
    logger.info(f"Scraping URL: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    return text

def chunk_text(text, target_words=400, overlap_percentage=0.25):

    logger.info(f"Starting text chunking: target={target_words} words, overlap={overlap_percentage*100:.0f}%")

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    logger.debug(f"Document split into {len(sentences)} sentences.")

    chunks = []
    cur = []
    cur_words = 0
    overlap = int(target_words * overlap_percentage)

    for s in sentences:
        s_words = len(s.split())
        if cur_words + s_words >= target_words:
            # add the cur to chunks[]
            chunks.append(" ".join(cur))
            # overlap_words will hold sentences to carry over into the next chunk.
            overlap_words = []
            while sum(len(w.split()) for w in overlap_words) < overlap and cur:
                overlap_words.insert(0, cur.pop())
            cur = overlap_words.copy()
            cur_words = sum(len(s.split()) for s in cur)
        cur.append(s)
        cur_words += s_words

    if cur:
        chunks.append(" ".join(cur))

    logger.info(f"Chunking complete: created {len(chunks)} chunks.")
    return chunks

def recursive_chunk_text(
    text,
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " "],
):
    def split_text(text, separators):
        if len(text) <= chunk_size:
            return [text]

        if not separators:
            return [text[:chunk_size], text[chunk_size:]]

        sep = separators[0]
        pieces = text.split(sep)

        chunks = []
        current = ""

        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue

            if len(current) + len(piece) + len(sep) <= chunk_size:
                current += piece + sep
            else:
                if current:
                    chunks.append(current.strip())
                current = piece + sep

        if current:
            chunks.append(current.strip())

        # If chunks are still too large, recurse with next separator
        final_chunks = []
        for c in chunks:
            if len(c) > chunk_size:
                final_chunks.extend(split_text(c, separators[1:]))
            else:
                final_chunks.append(c)

        return final_chunks

    raw_chunks = split_text(text, separators)

    # Add overlap
    final_chunks = []
    for i, chunk in enumerate(raw_chunks):
        if i == 0:
            final_chunks.append(chunk)
        else:
            overlap_text = raw_chunks[i - 1][-chunk_overlap:]
            final_chunks.append(overlap_text + chunk)

    return final_chunks

def paragraph_sentence_chunk_text(
    text,
    chunk_size=800,
    chunk_overlap=150,
):
    logger.info(f"text length: {len(text)}")
    logger.info(repr(text[:300]))
    """
    Paragraph-first, sentence-aware chunking.
    Each paragraph is treated as an atomic chunk unless it exceeds chunk_size.
    """

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []

    for para in paragraphs:
        # Case 1: Paragraph fits → keep it intact
        if len(para) <= chunk_size:
            chunks.append(para)

        # Case 2: Paragraph too large → split by sentences
        else:
            doc = nlp(para)
            sentence_chunk = ""

            for sent in doc.sents:
                s = sent.text.strip()
                if len(sentence_chunk) + len(s) <= chunk_size:
                    sentence_chunk += s + " "
                else:
                    chunks.append(sentence_chunk.strip())
                    sentence_chunk = s + " "

            if sentence_chunk:
                chunks.append(sentence_chunk.strip())

    # Add overlap
    final_chunks = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            final_chunks.append(chunk)
        else:
            overlap_text = chunks[i - 1][-chunk_overlap:]
            final_chunks.append(overlap_text + chunk)

    return final_chunks

def write_chunks_to_file(chunks, document_name):
    # base_name = os.path.splitext(document_name)[0]
    output_path = os.path.join(CHUNK_DEBUG_DIR, f"{document_name}_chunks.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"===== Document: {document_name} | Chunk {i+1} =====\n")
            f.write(chunk)
            f.write("\n\n")

    logger.info(f"Chunk debug file saved to: {output_path}")
    

if __name__ == "__main__":
    from pathlib import Path

    pdf_path = Path(__file__).parent.parent / "docs" / "hpb-2022_2023-annual-report.pdf"
    text = pdf_to_text(str(pdf_path))
    logger.info("Extracted text (first 500 chars):")
    logger.info(text[:500])

    # chunks = chunk_text(text)
    chunks = paragraph_sentence_chunk_text(
    text,
    chunk_size=800,
    chunk_overlap=150
    )
    logger.info(f"\nNumber of chunks: {len(chunks)}")
    logger.info("First chunk preview:")
    logger.info(chunks[0][:500])
