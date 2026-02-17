import logging
from ollama import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Llama27BModel:
    def __init__(self, model="llama2:7b-chat-q4"):
        self.client = Client()
        self.model = model

    def generate(self, prompt):
        logger.info("Running query on llama")
        response = self.client.chat(model=self.model, messages=[
            {"role": "user", "content": prompt}
        ])
        answer = response["message"]["content"]
        return answer
