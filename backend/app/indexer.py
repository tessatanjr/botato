# 1. Takes chunks of text (from ingest.py).
# 2. embed_text() Converts them into numerical embeddings using OpenAI’s text-embedding-3-small.
#       Each embedding is a 1536-dimensional vector (basically a list of 1536 numbers that represent the meaning of the text).
# 3. add_chunks_to_index() stores the vectors in a FAISS index.
#       FAISS is a vector database that allows you to quickly search for “nearest neighbors” (most semantically similar chunks).
# 4. save_index() keeps metadata alongside each vector.
#       Example: the original chunk text, which PDF it came from, and its position.
# 5. Optionally saves the index + metadata to disk so you can reload it later without recomputing embeddings.

import faiss
import numpy as np
import pickle
import logging
from app.config import EMBEDDING_PROVIDER,OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- OpenAI setup ---
if EMBEDDING_PROVIDER == "openai":
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    embedding_dim = 1536 # text-embedding-3-small output size
# --- Sentence Transformers setup ---
else:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding_dim = model.get_sentence_embedding_dimension() # will be 384

# create a FAISS index
index = faiss.IndexFlatL2(embedding_dim)
metadata_store = []  # List of dicts with chunk text, source, page, etc.

def embed_text(text):
    logger.info("Embedding text...")
    if EMBEDDING_PROVIDER == "openai":
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(resp.data[0].embedding, dtype="float32")
    else:
        return model.encode(text, convert_to_numpy=True)

def add_chunks_to_index(chunks, source="unknown"):
    logger.info(f"Adding {len(chunks)} chunks to FAISS index...")
    for i, chunk in enumerate(chunks):
        vector = embed_text(chunk)
        if EMBEDDING_PROVIDER == "openai":
            index.add([vector])
        else:
            vector = np.array(vector, dtype="float32").reshape(1, -1)
            index.add(vector)
        metadata_store.append({"source": source, "chunk_id": i, "text": chunk})
        logger.debug(f"Chunk {i} added: {chunk[:50]}...")  # first 50 chars
    
def save_index(index_file="data/faiss.index", meta_file="data/meta.pkl"):
    
    faiss.write_index(index, index_file)
    with open(meta_file, "wb") as f:
        pickle.dump(metadata_store, f)

    logger.info(f"FAISS index saved to {index_file}")
    logger.info(f"Metadata saved to {meta_file}")

if __name__ == "__main__":
    import ingest

    # 1. Load text & chunk it
    text = ingest.pdf_to_text("../docs/hpb-2022_2023-annual-report.pdf")
    chunks = ingest.chunk_text(text)

    print(f"Extracted {len(chunks)} chunks from PDF.")

    # 2. Add chunks to FAISS
    add_chunks_to_index(chunks, source="sample.pdf")
    print(f"FAISS index now contains {index.ntotal} vectors.")

    # 3. Save index + metadata
    save_index()
    print("Index and metadata saved to faiss.index and meta.pkl.")

    # 4. Inspect the first entry
    print("First metadata entry:\n", metadata_store[0])
