import faiss
import logging
import numpy as np
import os
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseIndexer:
    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim
        # self.index = faiss.IndexFlatL2(embedding_dim)
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.metadata_store = []

    def embed_text(self, text):
        """Implemented by openai/minilm child classes."""
        raise NotImplementedError

    def add_chunks_to_index(self, chunks, source="unknown"):
        for i, chunk in enumerate(chunks):
            vector = self.embed_text(chunk)
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
            # self.index.add(vector.astype("float32"))

            vector = vector.astype("float32")

            faiss.normalize_L2(vector)

            self.index.add(vector)

            self.metadata_store.append({
                "source": source,
                "chunk_id": i,
                "text": chunk
            })
        logger.info(f"Added {len(chunks)} chunks to FAISS index.")

    BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

    def get_index_paths(self, embedding_provider: str):
        """Return paths for FAISS index and metadata based on embedding provider."""
        index_dir = os.path.join(self.BASE_DIR, "indexes", embedding_provider.lower())
        os.makedirs(index_dir, exist_ok=True)
        
        index_file = os.path.join(index_dir, "faiss.index")
        meta_file = os.path.join(index_dir, "meta.pkl")
        return index_file, meta_file

    def save_index(self, embedding_provider: str):
        index_file, meta_file = self.get_index_paths(embedding_provider)
        faiss.write_index(self.index, index_file)
        with open(meta_file, "wb") as f:
            pickle.dump(self.metadata_store, f)
        logger.info(f"FAISS index saved to {index_file}")
        logger.info(f"Metadata saved to {meta_file}")
    
    def load_index(self, embedding_provider: str):
        index_file, meta_file = self.get_index_paths(embedding_provider)

        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
            with open(meta_file, "rb") as f:
                self.metadata_store = pickle.load(f)
            logger.info(f"Loaded existing index for {embedding_provider}")
        else:
            logger.info(f"No existing index found for {embedding_provider}, creating new one")

    def reset_index(self, embedding_provider: str):
        index_file, meta_file = self.get_index_paths(embedding_provider)

        if os.path.exists(index_file):
            os.remove(index_file)
        if os.path.exists(meta_file):
            os.remove(meta_file)

        # self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.metadata_store = []

        logger.info(f"Index reset for provider: {embedding_provider}")
