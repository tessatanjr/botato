# The retriever connects user questions to your document knowledge base.
# 1. Take a query (user question).

# 2. Find the most relevant chunks from your FAISS index.

# 3. Build a prompt with those chunks and ask GPT-4 to answer.

from openai import OpenAI
import logging
import os
from dotenv import load_dotenv
import faiss
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

index = faiss.read_index("data/faiss.index")
with open("data/meta.pkl", "rb") as f:
    metadata_store = pickle.load(f)
logger.info("Loading FAISS index from data/faiss.index")
logger.info("Loading metadata from data/meta.pkl")

def embed_query(query):
    logger.debug("Embedding query: %s", query)
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    vector = resp.data[0].embedding
    logger.debug("Query embedding obtained (length %d)", len(vector))
    return vector

def retrieve_chunks(query, k=5):
    logger.info("Retrieving top %d chunks for query: %s", k, query)
    q_vector = embed_query(query)
    D, I = index.search([q_vector], k)
    results = [metadata_store[i]["text"] for i in I[0]]
    logger.info("Retrieved %d chunks", len(results))
    return results

def rag_query(query):
    logger.info("Running RAG query")
    chunks = retrieve_chunks(query)
    context = "\n".join(chunks)
    prompt = f"""
You are a helpful assistant. Use the following context to answer the question.
Context:
{context}
Question: {query}

If the answer is not in the context, say "I don't know."
"""
    logger.debug("RAG prompt constructed (first 500 chars): %s", prompt[:500])
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message["content"]
    logger.info("RAG query completed, answer length: %d", len(answer))
    return answer

