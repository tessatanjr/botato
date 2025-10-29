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

import logging
import pdfplumber
import spacy

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# integrate pdf2image + pytesseract later for scanned PDFs

# NLP model setup
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model 'en_core_web_sm' loaded successfully.")
except OSError:
    logger.warning("spaCy model not found. Downloading...")
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def pdf_to_text(path):
    logger.info(f"Starting text extraction from PDF: {path}")   

    text = ""

    page_count = 0

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_count += 1
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                logger.warning(f"No extractable text found on page {page.page_number}")
    logger.info(f"Extracted text from {page_count} pages ({len(text)} characters total).")
    return text

def chunk_text(text, target_words=400, overlap_pct=0.25):

    logger.info(f"Starting text chunking: target={target_words} words, overlap={overlap_pct*100:.0f}%")

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    logger.debug(f"Document split into {len(sentences)} sentences.")

    chunks = []
    cur = []
    cur_words = 0
    overlap = int(target_words * overlap_pct)

    for s in sentences:
        s_words = len(s.split())
        if cur_words + s_words >= target_words:
            chunks.append(" ".join(cur))
            # naive overlap: last sentences
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

if __name__ == "__main__":
    from pathlib import Path

    pdf_path = Path(__file__).parent.parent / "docs" / "hpb-2022_2023-annual-report.pdf"
    text = pdf_to_text(str(pdf_path))
    logger.info("Extracted text (first 500 chars):")
    logger.info(text[:500])

    chunks = chunk_text(text)
    logger.info(f"\nNumber of chunks: {len(chunks)}")
    logger.info("First chunk preview:")
    logger.info(chunks[0][:500])
