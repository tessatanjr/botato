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
    # below version faster ingest by 5-10 times, since POS/NER tagging, lemmatization and dependency parsing not needed
    # nlp = spacy.load("en_core_web_sm")

    # only does tokenisation + sentence segmentation
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    logger.info("spaCy model 'en' loaded successfully.")
except OSError:
    logger.warning(f"Failed to load spaCy model: {e}")
    logger.info("Please make sure spaCy is installed and models are available.")

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
    """
    Recursive character-based text splitter.
    Similar to LangChain's RecursiveCharacterTextSplitter.
    """

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


if __name__ == "__main__":
    from pathlib import Path

    pdf_path = Path(__file__).parent.parent / "docs" / "hpb-2022_2023-annual-report.pdf"
    text = pdf_to_text(str(pdf_path))
    logger.info("Extracted text (first 500 chars):")
    logger.info(text[:500])

    # chunks = chunk_text(text)
    chunks = recursive_chunk_text(
    text,
    chunk_size=800,
    chunk_overlap=150
    )
    logger.info(f"\nNumber of chunks: {len(chunks)}")
    logger.info("First chunk preview:")
    logger.info(chunks[0][:500])
