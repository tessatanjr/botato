from sentence_transformers import SentenceTransformer
from app.indexing.base_indexer import BaseIndexer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MiniLMIndexer(BaseIndexer):
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding_dim = self.model.get_sentence_embedding_dimension()
        super().__init__(embedding_dim=embedding_dim)

    def embed_text(self, text):
        logger.info("Embedding with MiniLM-L6 (sentence-transformers)...")
        return self.model.encode(text, convert_to_numpy=True)
