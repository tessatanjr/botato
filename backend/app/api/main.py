from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.ingest.ingest import pdf_to_text, recursive_chunk_text
from app.indexing.openai_indexer import OpenAIIndexer
from app.indexing.minilm_indexer import MiniLMIndexer
# from backend.app.indexing.indexer import add_chunks_to_index, save_index
from app.retrieval.retrieval import RetrievalEngine
from app.llm.gpt import GPTModel
from app.llm.LLaMa import LlamaModel
import shutil, os

app = FastAPI()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class ChatRequest(BaseModel):
    question: str
    top_k: int = 5
    llm_model: str = "gpt-4"           
    embedding_provider: str = "openai"

def get_indexer(provider: str):
    if provider.lower() == "openai":
        return OpenAIIndexer()
    elif provider.lower() == "minilm":
        return MiniLMIndexer()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported embedding provider: {provider}")

@app.get("/")
def read_root():
    return {"message": "Hello BOTATO!"}

@app.post("/api/chat")
def chat(req: ChatRequest):

    retriever = RetrievalEngine(provider=req.embedding_provider)

    context_chunks = retriever.retrieve_chunks(req.question, k=req.top_k)
    context_text = "\n".join(context_chunks)

    if req.llm_model.lower().startswith("gpt"):
        llm = GPTModel(model=req.llm_model)
    elif req.llm_model.lower().startswith("llama"):
        llm = LlamaModel(model=req.llm_model)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported LLM model: {req.llm_model}")

    prompt = f"""
You are a helpful assistant. Use the following context to answer the question.
If the answer is not in the context, say "I don't know."

Context:
{context_text}

Question: {req.question}
"""

    answer = llm.generate(prompt)

    return {"question": req.question, "answer": answer}

@app.post("/api/retrieve")
def retrieve_only(req: ChatRequest):
    retriever = RetrievalEngine(provider=req.embedding_provider)
    results = retriever.retrieve_chunks(req.question, top_k=req.top_k)
    return {"query": req.question, "results": results}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...), embedding_provider: str = Form("openai")):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save uploaded file locally
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Step 1: Extract text
    text = pdf_to_text(file_path)

    # Step 2: Chunk text
    # chunks = chunk_text(text)
    # chunks = chunk_text(text, target_words=200, overlap_percentage=0.1)
    chunks = recursive_chunk_text(
    text,
    chunk_size=1000,
    chunk_overlap=150
    )

    # Step 3: Embed and add to FAISS
    indexer = get_indexer(embedding_provider)
    indexer.load_index(embedding_provider)
    indexer.add_chunks_to_index(chunks, source=file.filename)
    indexer.save_index(embedding_provider)

    return {"message": f"{file.filename} uploaded and processed",
            "chunks_added": len(chunks),
            "embedding_provider": embedding_provider}

@app.post("/api/reset")
def reset_index(embedding_provider: str = "openai"):
    embedding_provider = embedding_provider.lower()

    if embedding_provider not in ["openai", "minilm"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported embedding provider: {embedding_provider}"
        )

    indexer = get_indexer(embedding_provider)
    indexer.reset_index(embedding_provider)

    return {
        "message": "Index reset successful",
        "embedding_provider": embedding_provider
    }
