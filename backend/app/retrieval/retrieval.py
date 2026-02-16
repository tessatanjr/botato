# The retriever connects user questions to your document knowledge base.
# 1. Take a query (user question).

# 2. Find the most relevant chunks from your FAISS index.

# 3. Build a prompt with those chunks and ask GPT-4 to answer.

from dotenv import load_dotenv
import faiss
import logging
import numpy as np
from openai import OpenAI
import os
import pickle
from sentence_transformers import SentenceTransformer

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrievalEngine:
    def __init__(self, provider="openai"):

        self.provider = provider.lower()

        base_path = f"data/indexes/{self.provider}"
        index_path = f"{base_path}/faiss.index"
        meta_path  = f"{base_path}/meta.pkl"

        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.index = faiss.read_index(index_path)
        logger.info(f"Loaded FAISS index from {index_path}")

        with open(meta_path, "rb") as f:
            self.metadata_store = pickle.load(f)
        logger.info(f"Loaded metadata store from {meta_path}")


        logger.info("Retrieval engine initialized.")

    def embed_query(self, query):
        logger.debug("Embedding query: %s", query)
        if self.provider == "openai":
            resp = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            return resp.data[0].embedding

        elif self.provider == "minilm":
            vector = self.model.encode(query)
            return vector.tolist()

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def retrieve_chunks(self, query, k=5):
        logger.info(f"Retrieving top {k} chunks for: {query}")

        vector = self.embed_query(query)

        query_vector = np.array(vector, dtype="float32").reshape(1, -1)

        faiss.normalize_L2(query_vector)

        D, I = self.index.search(query_vector, k)

        results = []
        
        for idx in I[0]:
            metadata = self.metadata_store[idx]
            results.append({
                "chunk_index": "Chunk " + str(metadata.get("chunk_id", idx)),
                "text": metadata["text"],
                "source": metadata.get("source", "unknown")
            })

        logger.info("Retrieved %d chunks", len(results))
        return results

    def build_context(self, query, k=5):
        """Retrieve chunks and join them as a context block."""
        chunks = self.retrieve_chunks(query, k)
        return "\n".join(chunks)