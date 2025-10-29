from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.ingest import pdf_to_text, chunk_text
from app.indexer import add_chunks_to_index, save_index
from app.retrieval import rag_query
import shutil
import os

app = FastAPI()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class ChatRequest(BaseModel):
    question: str
    top_k: int = 5

@app.get("/")
def read_root():
    return {"message": "Hello BOTATO!"}

@app.post("/api/chat")
def chat(req: ChatRequest):
    answer = rag_query(req.question)
    return {"question": req.question, "answer": answer}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save uploaded file locally
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Step 1: Extract text
    text = pdf_to_text(file_path)

    # Step 2: Chunk text
    chunks = chunk_text(text)

    # Step 3: Embed and add to FAISS
    add_chunks_to_index(chunks, source=file.filename)
    save_index()

    return {"message": f"{file.filename} uploaded and processed", "chunks_added": len(chunks)}
