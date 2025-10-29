import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence")  # default = sentence
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

