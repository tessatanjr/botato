# 🍠 Botato - No-code RAG chatbot builder

Botato is my Final Year Project that builds a low-cost, low-effort solution for creating customer-facing chatbots from messy and unstructured documents.

It is designed for SMEs, NGOs, and event planners who lack the technical expertise or resources to build chatbots, providing them with an end-to-end automated pipeline powered by GPT-4 and Retrieval-Augmented Generation (RAG).

With Botato, creating a chatbot is as simple as uploading documents — the system handles ingestion, preprocessing, indexing, and deployment.

## Features

- Multi-source document ingestion
  - PDFs (structured + scanned w/ OCR)
  - Web scraping (HTML pages)
  - Word documents (.docx)
- Text preprocessing and sentence segmentation with spaCy
- Paragraph-aware chunking with sentence-level overlap
- Vector embeddings & retrieval with FAISS (MiniLM + OpenAI Embeddings)
- GPT-4, GPT-5 (OpenAI API) and Llama 3 (Ollama, local)
- No-code interface to create and deploy chatbots
- Containerized with Docker for easy local setup

## Tech Stack

**Backend**

- FastAPI + Uvicorn
- pdfplumber, pytesseract, spaCy, BeautifulSoup4
- FAISS for vector storage
- OpenAI Embeddings + GPT-4 API

**Frontend**

- React 18 + Vite
- Tailwind CSS for styling
- Axios for HTTP communication with the backend
- Intentionally minimal — serves as a demonstration layer for the underlying retrieval and generation system

**Infrastructure**

- Docker + Docker Compose

## Getting Started

### Prerequisites

- Docker Desktop installed ([download here](https://www.docker.com/products/docker-desktop))
- An OpenAI API key

### Setup

1. Clone the repository

```bash
git clone https://github.com/tessatanjr/botato.git
cd botato
```

2.  Create a `.env` file in the `backend/` folder:

```
   OPENAI_API_KEY=your_openai_api_key_here
```

3. Run with Docker

```bash
   docker compose up --build
```

Backend will run at http://localhost:8000
Frontend will run at http://localhost:3000

> To stop the app, press `Ctrl+C` in the terminal.

## How to Use

Botato runs as a single-page application. The left side is the **chat interface** and the right side is the **document upload panel**.

### 1. Select your settings

At the top right, choose your:

- **Embedding model** — MiniLM (local, free) or OpenAI (higher accuracy)
- **LLM model** — GPT-4 or LLaMA3

### 2. Upload your documents

You have two options:

**Upload a file** — drag and drop PDF or .docx files into the upload panel, or click to browse.

**Scrape a webpage** — paste a URL into the input box and click **Add**. Botato will scrape and index the page content automatically.

> **Note:** If you want to index a document with both MiniLM and OpenAI embeddings, upload the document twice — once with each embedding model selected.

### 3. Index your documents

Click **Index Document**. Each document will be processed one by one. You can track progress via the status indicator:

- **Queued** — waiting to be processed
- **Indexed** — ready to query

### 4. Chat with your documents

Once a document is indexed, use the chat panel on the left to ask questions about your uploaded content.

The chatbot will respond using your selected LLM and show the **retrieved source chunks** in a dropdown below each response, so you can see exactly where the answer came from.

> If you ask about something not covered in your documents, the bot will respond with **"I don't know"** rather than hallucinating an answer.

## Authors

**Tessa Tan** — College of Computing and Data Science, Nanyang Technological University
