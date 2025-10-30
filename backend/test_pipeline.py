# to run this cd to backend/ and run command python -m app.test_pipeline 

from app.ingest import pdf_to_text, chunk_text
from app.indexer import add_chunks_to_index, save_index
# from app.retrieval import rag_query

# Step 1: Load PDF
text = pdf_to_text("docs/hpb-2022_2023-annual-report.pdf")
print("Extracted text preview:", text[:300], "\n---\n")

# Step 2: Chunking
chunks = chunk_text(text)
print(f"Created {len(chunks)} chunks")

# Step 3: Add chunks to FAISS index
add_chunks_to_index(chunks, source="sample.pdf")
save_index()

# Step 4: Ask GPT-4 using retrieval
# question = "What is this document about?"
# answer = rag_query(question)
# print("\nQ:", question)
# print("A:", answer)
