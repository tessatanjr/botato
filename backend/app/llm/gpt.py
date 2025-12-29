import logging
from openai import OpenAI
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class GPTModel:
    def __init__(self, model="gpt-4"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate(self, prompt):
        logger.info("Running query on gpt")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message["content"]
        logger.info("RAG query completed, answer length: %d", len(answer))
        return answer
