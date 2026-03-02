from app.retrieval.retrieval import RetrievalEngine

def test_retrieval():
    retriever = RetrievalEngine(provider="minilm")  

    query = "What are the benefits of payment methods?"
    chunks = retriever.retrieve_chunks(query, k=5)

    print("\nRetrieved Chunks:")
    for i, c in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---\n{c[:300]}")

if __name__ == "__main__":
    test_retrieval()


