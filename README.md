# 🍠 Botato - No-code RAG chatbot builder

Botato is my Final Year Project that builds a low-cost, low-effort solution for creating customer-facing chatbots from messy and unstructured documents.

It is designed for SMEs, NGOs, and event planners who lack the technical expertise or resources to build chatbots, providing them with an end-to-end automated pipeline powered by GPT-4 and Retrieval-Augmented Generation (RAG).

With Botato, creating a chatbot is as simple as uploading documents — the system handles ingestion, preprocessing, indexing, and deployment.


## Features

- Multi-source document ingestion
    - PDFs (structured + scanned w/ OCR)
    - Web scraping (HTML pages)
- Text preprocessing (tokenization, lemmatization, NER, stopword removal)
- Smart chunking with sliding window overlap
- Vector embeddings & retrieval with FAISS
- GPT-4 powered chatbot (via OpenAI API)
- No-code interface to create and deploy chatbots
- Containerized with Docker for portability


## Tech Stack

### Backend
FastAPI + Uvicorn
Python libraries: pdfplumber, pytesseract, spaCy, BeautifulSoup4
FAISS for vector database
OpenAI Embeddings + GPT-4 API

### Frontend
React (with Tailwind & shadcn/ui components)

### Cloud & Deployment
Docker containers for backend/frontend
Deployment-ready for cloud platforms


## Getting Started
1. Clone the repository
git clone https://github.com/tessatanjr/botato.git
cd botato

2. Backend Setup
cd backend
python -m venv botato-be
source botato-be/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

Backend will run at http://localhost:8000

3. Frontend Setup
cd frontend
npm install
npm run dev

Frontend will run at http://localhost:3000


## Authors

**Tessa Tan** — College of Computing and Data Science, Nanyang Technological University