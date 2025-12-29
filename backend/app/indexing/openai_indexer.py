from app.config import OPENAI_API_KEY
from app.indexing.base_indexer import BaseIndexer
import numpy as np
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIIndexer(BaseIndexer):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        super().__init__(embedding_dim=1536)

    def embed_text(self, text):
        logger.info("Embedding with OpenAI text-embedding-3-small...")
        resp = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(resp.data[0].embedding, dtype="float32")
    