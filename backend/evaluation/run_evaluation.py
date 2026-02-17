#!/usr/bin/env python3
"""
Simple RAG Evaluation Runner
Usage: python run_evaluation.py --provider minilm --model llama --top-k 6
"""

import argparse
from evaluate_rag import RAGEvaluator

def main():
    parser = argparse.ArgumentParser(description='Run RAG evaluation')
    parser.add_argument('--questions', type=str, default='golden_question_set.json',
                        help='Path to questions JSON file')
    parser.add_argument('--provider', type=str, default='minilm',
                        choices=['minilm', 'openai'],
                        help='Embedding provider (minilm or openai)')
    parser.add_argument('--model', type=str, default='gpt-4',
                        help='LLM model to use (e.g., gpt-4, llama27b, llama213b')
    parser.add_argument('--top-k', type=int, default=5,
                        help='Number of chunks to retrieve')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file path (optional, auto-generated if not provided)')
    parser.add_argument('--base-url', type=str, default='http://127.0.0.1:8000',
                        help='Base URL of the API')
    
    args = parser.parse_args()
    
    evaluator = RAGEvaluator(base_url=args.base_url)
    
    evaluator.run_evaluation(
        questions_file=args.questions,
        embedding_provider=args.provider,
        llm_model=args.model,
        top_k=args.top_k,
        output_file=args.output
    )

if __name__ == "__main__":
    main()
