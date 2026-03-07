# RAG Chatbot Evaluation Guide

## Description

This set of tests is designed to determine which LLM + embedder combo is most ideal for my RAG chatbot. Effectiveness is measured using three key metrics:

1. **Recall@K**: how many relevant chunks were retrieved (top k = 6)
2. **Mean Reciprocal Rank (MRR)**: the rank position of the first relevant chunk
3. **F1 Score**: the quality of generated answers compared to golden answers by precision and recall

## Files

- `evaluate_rag.py`: Main evaluation script
- `run_evaluation.py`: command-line runner
- `golden_question_set.json`: Golden set of question answer pairs and correct chunks to be retrieved

## Prerequisites

1. **Install required packages**:
```bash
pip install requests pandas matplotlib seaborn
```

2. **Start FastAPI server**:
```bash
uvicorn app.api.main:app --reload
```

3. **Verify the server is running**:
```bash
curl http://127.0.0.1:8000/
```

## Step-by-Step Instructions

### Step 1: Prepare Your Questions File

Make sure questions file is in the correct path and is in this format:
```bash
{
        "id": "SFAQ-01",
        "question": "What is my Stripe account username?",
        "golden_answer": "Your Stripe account username is the email address you used to register.",
        "openai_relevant_chunk": [
            "Chunk 1"
        ],
        "minilm_relevant_chunk": [
            "Chunk 1"
        ],
        "source_document": "stripe_faq_24p.pdf"
    },
```

### Step 2: Run eval using run_evaluation.py
```bash
# Evaluate with MinILM embeddings
python run_evaluation.py --provider minilm --model llama3:latest --top-k 6
python run_evaluation.py --provider minilm --model gpt-4 --top-k 6
python run_evaluation.py --provider minilm --model gpt-5 --top-k 6

# Evaluate with OpenAI embeddings
python run_evaluation.py --provider openai --model llama3:latest --top-k 6
python run_evaluation.py --provider openai --model gpt-4 --top-k 6
python run_evaluation.py --provider openai --model gpt-5 --top-k 6
```

### Step 3: Output

Results will be print and saved to JSON files:
(evaluation_results_minilm_gpt_4_20260218_144201.json)(evaluation_results_minilm_gpt_5_20260218_182833.json)(evaluation_results_minilm_llama3:latest_20260218_164923.json)(evaluation_results_openai_gpt_4_20260218_141617.json)(evaluation_results_openai_gpt_5_20260218_192232.json) (evaluation_results_openai_llama3:latest_20260218_161339.json)


### Step 4: Understand the Metrics

#### Recall@K
- **Range**: 0.0 to 1.0 (higher better)
- **Meaning**: What fraction of relevant chunks were retrieved?
- **Example**: If 2 out of 3 relevant chunks were retrieved, Recall@3 = 0.667

#### Mean Reciprocal Rank (MRR)
- **Range**: 0.0 to 1.0 (higher is better)
- **Meaning**: How highly ranked was the first relevant chunk?
- **Example**: 
  - First relevant chunk at position 1 → MRR = 1.0
  - First relevant chunk at position 2 → MRR = 0.5
  - First relevant chunk at position 3 → MRR = 0.333

#### F1 Score
- **Range**: 0.0 to 1.0 (higher is better)
- **Meaning**: Balance between precision and recall of the answer text
- **Calculation**: Token-level overlap between predicted and golden answers
