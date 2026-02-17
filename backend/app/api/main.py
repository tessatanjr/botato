from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from db.session import SessionLocal
from sqlalchemy.orm import Session
from db.model import ChatMessage, ChatSession, Document, DocumentChunk
import glob
from pydantic import BaseModel
from app.ingest.ingest import pdf_to_text, paragraph_sentence_chunk_text, write_chunks_to_file, CHUNK_DEBUG_DIR
from app.indexing.openai_indexer import OpenAIIndexer
from app.indexing.minilm_indexer import MiniLMIndexer
# from backend.app.indexing.indexer import add_chunks_to_index, save_index
from app.retrieval.retrieval import RetrievalEngine
from app.llm.gpt import GPTModel
from backend.app.llm.llama27b import Llama27BModel
from backend.app.llm.llama213b import Llama213BModel
import shutil, os

app = FastAPI()

# UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "docs")
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class ChatRequest(BaseModel):
    session_id: int
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

    db= SessionLocal()

    user_message = ChatMessage(
        session_id=req.session_id,
        role="user",
        content=req.question
    )
    db.add(user_message)
    db.commit()

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == req.session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(6)
        .all()
    )

    messages.reverse()

    conversation = ""
    for m in messages:
        conversation += f"{m.role}: {m.content}\n"

    retriever = RetrievalEngine(provider=req.embedding_provider)

    retrieved = retriever.retrieve_chunks(req.question, k=req.top_k)
    context_text = "\n\n".join([c["text"] for c in retrieved])
    retrieved_chunk_info = [
        {
            "index": r["chunk_index"],
            "source": r["source"]
        }
        for r in retrieved
    ]

    if req.llm_model.lower().startswith("gpt"):
        llm = GPTModel(model="gpt-4")
    elif req.llm_model.lower().startswith("llama27b"):
        llm = Llama27BModel(model="llama2:7b-chat-q4")
    elif req.llm_model.lower().startswith("llama213b"):
        llm = Llama213BModel(model="llama2:13b-chat-q4")
    else:
        db.close()
        raise HTTPException(status_code=400, detail=f"Unsupported LLM model: {req.llm_model}")

    prompt = f"""
    You are a helpful assistant for answering questions based ONLY on the provided context.

    Instructions:
    - Use ONLY the information in the Relevant context to answer the question.
    - Also use the Conversation so far for understanding the user's intent, but DO NOT use it as a source of factual information.
    - If the answer is not explicitly stated in the context, reply with: "I don't know."
    - Do NOT use prior knowledge or make assumptions.
    - Keep the answer concise, factual, and directly relevant to the question.

    Conversation so far:
    {conversation}

    Relevant context:
    {context_text}

    User question:
    {req.question}

    Answer:
    """
    answer = llm.generate(prompt)

    assistant_msg = ChatMessage(
        session_id=req.session_id,
        role="assistant",
        content=answer
    )
    db.add(assistant_msg)
    db.commit()
    db.close()

    return {"question": req.question, "answer": answer, "retrieved_chunks": retrieved_chunk_info}

# creates chat session entry in db
@app.post("/api/chat/start")
def start_chat():
    db = SessionLocal()
    session = ChatSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    db.close()

    return {"session_id": session.id}

@app.post("/api/retrieve")
def retrieve_only(req: ChatRequest):
    retriever = RetrievalEngine(provider=req.embedding_provider)
    results = retriever.retrieve_chunks(req.question, top_k=req.top_k)
    return {"query": req.question, "results": results}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...), embedding_provider: str = Form("openai")):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Extract 
    text = pdf_to_text(file.file)

    # chunk
    if embedding_provider.lower() == "openai":
        chunk_size = 2000
        chunk_overlap = 250
    elif embedding_provider.lower() == "minilm":
        chunk_size = 1000
        chunk_overlap = 150
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported embedding provider: {embedding_provider}"
        )
    chunks = paragraph_sentence_chunk_text(
        text,
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )

    # Embed and save to FAISS
    indexer = get_indexer(embedding_provider)
    indexer.load_index(embedding_provider)
    indexer.add_chunks_to_index(chunks, source=file.filename)
    indexer.save_index(embedding_provider)

    # save to local
    write_chunks_to_file(
        chunks,
        f"{file.filename}_{embedding_provider}"
    )

    # save to db
    db = SessionLocal()

    doc = Document(
        filename=file.filename,
        embedding_provider=embedding_provider,
        chunk_strategy="paragraph_sentence",
        num_chunks=len(chunks)
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    for i, chunk in enumerate(chunks):
        db_chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=i,
            text=chunk
        )
        db.add(db_chunk)

    db.commit()
    db.close()

    print(f"Total chunks: {len(chunks)}\n")

    return {"message": f"{file.filename} uploaded and processed",
            "chunks_added": len(chunks),
            "embedding_provider": embedding_provider}

@app.get("/api/inspect/db")
def inspect_db(limit_chunks: int = 3):
    # check all documents present in db and how many chunks to show (limit_chunks)

    db: Session = SessionLocal()

    try:
        documents = db.query(Document).all()
        results = []

        for doc in documents:
            chunks = (
                db.query(DocumentChunk)
                .filter(DocumentChunk.document_id == doc.id)
                .order_by(DocumentChunk.chunk_index)
                .limit(limit_chunks)
                .all()
            )

            results.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "embedding_provider": doc.embedding_provider,
                "chunk_strategy": doc.chunk_strategy,
                "num_chunks": doc.num_chunks,
                "sample_chunks": [
                    {
                        "chunk_index": c.chunk_index,
                        "preview": c.text[:200] 
                    }
                    for c in chunks
                ]
            })

        return {
            "total_documents": len(results),
            "documents": results
        }

    finally:
        db.close()

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

    chunk_files = glob.glob(f"{CHUNK_DEBUG_DIR}/*_chunks.txt")
    for f in chunk_files:
        os.remove(f)

    db: Session = SessionLocal()

    try:
        docs = (
            db.query(Document)
            .filter(Document.embedding_provider == embedding_provider)
            .all()
        )

        doc_ids = [doc.id for doc in docs]

        if doc_ids:
            db.query(DocumentChunk)\
              .filter(DocumentChunk.document_id.in_(doc_ids))\
              .delete(synchronize_session=False)

            db.query(Document)\
              .filter(Document.id.in_(doc_ids))\
              .delete(synchronize_session=False)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

    return {
        "message": "Index reset successful",
        "embedding_provider": embedding_provider
    }
