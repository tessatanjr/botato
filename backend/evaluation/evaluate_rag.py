import requests
import json
import time
from typing import List, Dict, Tuple
from datetime import datetime
import re
from collections import Counter

class RAGEvaluator:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        
    def start_session(self) -> int:
        """Start a new chat session"""
        response = requests.post(f"{self.base_url}/api/chat/start")
        response.raise_for_status()
        session_id = response.json()["session_id"]
        print(f"Started session: {session_id}")
        return session_id
    
    def query_chatbot(self, session_id, question: str, embedding_provider: str, llm_model: str, top_k: int) -> Dict:
        """Query the chatbot endpoint"""
        payload = {
            "question": question,
            "session_id": session_id,
            "embedding_provider": embedding_provider,
            "llm_model": llm_model,
            "top_k": top_k
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def normalize_chunk_id(self, chunk_id: str) -> str:
        """Normalize chunk IDs to handle different formats (e.g., 'Chunk 1', 'Chunk 0')"""
        # Extract number from chunk ID
        match = re.search(r'\d+', chunk_id)
        if match:
            return f"Chunk {match.group()}"
        return chunk_id
    
    def calculate_recall_at_k(self, retrieved_chunks: List[str], golden_chunks: List[str]) -> float:
        """
        Calculate Recall@K
        Recall@K = (number of relevant chunks retrieved) / (total number of relevant chunks)
        """
        if not golden_chunks:
            return 1.0
        
        # Normalize chunk IDs
        retrieved_normalized = set(self.normalize_chunk_id(c) for c in retrieved_chunks)
        golden_normalized = set(self.normalize_chunk_id(c) for c in golden_chunks)
        
        # relevant_retrieved = len(retrieved_normalized.intersection(golden_normalized))
        # total_relevant = len(golden_normalized)
        
        # return relevant_retrieved / total_relevant if total_relevant > 0 else 0.0
        hit = retrieved_normalized.intersection(golden_normalized)

        return 1.0 if hit else 0.0
    
    def calculate_mrr(self, retrieved_chunks: List[str], golden_chunks: List[str]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR)
        MRR = 1 / rank of first relevant chunk
        """
        if not golden_chunks:
            return 1.0
        
        # Normalize chunk IDs
        golden_normalized = set(self.normalize_chunk_id(c) for c in golden_chunks)
        
        for rank, chunk in enumerate(retrieved_chunks, start=1):
            normalized_chunk = self.normalize_chunk_id(chunk)
            if normalized_chunk in golden_normalized:
                return 1.0 / rank
        
        return 0.0  # No relevant chunk found
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization for F1 score calculation"""
        # Convert to lowercase and split on whitespace/punctuation
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def calculate_f1_score(self, predicted_answer: str, golden_answer: str) -> Tuple[float, float, float]:
        """
        Calculate token-level F1 score between predicted and golden answers
        Returns: (precision, recall, f1_score)
        """
        pred_tokens = self.tokenize(predicted_answer)
        gold_tokens = self.tokenize(golden_answer)
        
        if not pred_tokens or not gold_tokens:
            return 0.0, 0.0, 0.0
        
        pred_counter = Counter(pred_tokens)
        gold_counter = Counter(gold_tokens)
        
        # Calculate true positives
        common = pred_counter & gold_counter
        num_same = sum(common.values())
        
        if num_same == 0:
            return 0.0, 0.0, 0.0
        
        precision = num_same / len(pred_tokens)
        recall = num_same / len(gold_tokens)
        f1 = 2 * (precision * recall) / (precision + recall)
        
        return precision, recall, f1
    
    def calculate_token_recall(self, predicted_answer: str, golden_answer: str) -> float:
        """
        Measures how much of the golden answer is covered by the model output.
        Equivalent to token-level recall.
        """

        pred_tokens = self.tokenize(predicted_answer)
        gold_tokens = self.tokenize(golden_answer)

        if not gold_tokens:
            return 1.0  # nothing required → perfect recall

        pred_counter = Counter(pred_tokens)
        gold_counter = Counter(gold_tokens)

        common = pred_counter & gold_counter
        num_same = sum(common.values())

        return num_same / len(gold_tokens)
    
    def run_evaluation(
        self,
        questions_file: str,
        embedding_provider: str = "minilm",
        llm_model: str = "gpt-4",
        top_k: int = 5,
        output_file: str = None
    ) -> Dict:
        """
        Run complete evaluation pipeline
        """
        # Load questions
        with open(questions_file, 'r') as f:
            questions_data = json.load(f)
        
        print(f"\nLoaded {len(questions_data)} questions")
        print(f"Embedding provider: {embedding_provider}")
        print(f"LLM model: {llm_model}")
        print(f"Top K: {top_k}\n")
        
        # Start session
        
        results = []
        recall_scores = []
        mrr_scores = []
        f1_scores = []
        precision_scores = []
        recall_f1_scores = []
        token_recall_scores = []

        
        # Process each question
        for idx, item in enumerate(questions_data, 1):
            session_id = self.start_session()

            print(f"Processing {idx}/{len(questions_data)}: {item['id']}")
            
            try:
                # Query the chatbot
                response = self.query_chatbot(
                    session_id=session_id,
                    question=item['question'],
                    embedding_provider=embedding_provider,
                    llm_model=llm_model,
                    top_k=top_k
                )
                
                # Extract retrieved chunk indices
                retrieved_chunk_ids = [chunk['index'] for chunk in response['retrieved_chunks']]
                
                # Get golden chunks based on embedding provider
                if embedding_provider.lower() == "openai":
                    golden_chunks = item.get('openai_relevant_chunk', [])
                else:
                    golden_chunks = item.get('minilm_relevant_chunk', [])
                
                # Calculate metrics
                recall = self.calculate_recall_at_k(retrieved_chunk_ids, golden_chunks)
                mrr = self.calculate_mrr(retrieved_chunk_ids, golden_chunks)
                precision, recall_f1, f1 = self.calculate_f1_score(
                    response['answer'],
                    item['golden_answer']
                )

                token_recall = self.calculate_token_recall(
                    response['answer'],
                    item['golden_answer']
                )

                # Store results
                result = {
                    'question_id': item['id'],
                    'question': item['question'],
                    'golden_answer': item['golden_answer'],
                    'predicted_answer': response['answer'],
                    'golden_chunks': golden_chunks,
                    'retrieved_chunks': retrieved_chunk_ids,
                    'source_document': item['source_document'],
                    'metrics': {
                        'recall_at_k': recall,
                        'mrr': mrr,
                        'f1_score': f1,
                        'precision': precision,
                        'recall': recall_f1,
                        'token_recall':token_recall
                    }
                }
                
                results.append(result)
                recall_scores.append(recall)
                mrr_scores.append(mrr)
                f1_scores.append(f1)
                precision_scores.append(precision)
                recall_f1_scores.append(recall_f1)
                token_recall_scores.append(token_recall)
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing {item['id']}: {str(e)}")
                continue
        
        # Calculate aggregate metrics
        aggregate_metrics = {
            'total_questions': len(questions_data),
            'successful_queries': len(results),
            'failed_queries': len(questions_data) - len(results),
            'average_recall_at_k': sum(recall_scores) / len(recall_scores) if recall_scores else 0,
            'average_mrr': sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0,
            'average_f1_score': sum(f1_scores) / len(f1_scores) if f1_scores else 0,
            'average_precision': sum(precision_scores) / len(precision_scores) if precision_scores else 0,
            'average_recall': sum(recall_f1_scores) / len(recall_f1_scores) if recall_f1_scores else 0,
            'average_token_recall': sum(token_recall_scores) / len(token_recall_scores) if token_recall_scores else 0,
        }
        
        # Prepare final output
        final_output = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'embedding_provider': embedding_provider,
                'llm_model': llm_model,
                'top_k': top_k,
                'questions_file': questions_file
            },
            'aggregate_metrics': aggregate_metrics,
            'detailed_results': results
        }
        
        # Save to file
        if output_file is None:
            output_file = f"evaluation_results_{embedding_provider}_{llm_model.replace('-', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(final_output, f, indent=2)
        
        print(f"\n{'='*60}")
        print("EVALUATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Questions: {aggregate_metrics['total_questions']}")
        print(f"Successful: {aggregate_metrics['successful_queries']}")
        print(f"Failed: {aggregate_metrics['failed_queries']}")
        print(f"\nRetrieval Metrics:")
        print(f"  Average Recall@{top_k}: {aggregate_metrics['average_recall_at_k']:.4f}")
        print(f"  Average MRR: {aggregate_metrics['average_mrr']:.4f}")
        print(f"\nAnswer Quality Metrics:")
        print(f"  Average F1 Score: {aggregate_metrics['average_f1_score']:.4f}")
        print(f"  Average Answer Recall: {aggregate_metrics['average_answer_recall']:.4f}")
        print(f"  Average Precision: {aggregate_metrics['average_precision']:.4f}")
        print(f"  Average Token Recall: {aggregate_metrics['average_token_recall']:.4f}")
        print(f"\nResults saved to: {output_file}")
        print(f"{'='*60}\n")
        
        return final_output


def main():
    """
    Main execution function
    """
    evaluator = RAGEvaluator(base_url="http://127.0.0.1:8000")
    
    # Example: Run evaluation with different configurations
    
    # Configuration 1: MinILM embeddings with GPT-4
    print("Running evaluation with MinILM + GPT-4...")
    evaluator.run_evaluation(
        questions_file="evaluation_questions.json",
        embedding_provider="minilm",
        llm_model="gpt-4",
        top_k=5,
        output_file="results_minilm_gpt4.json"
    )
    
    # Configuration 2: OpenAI embeddings with GPT-4
    print("\nRunning evaluation with OpenAI + GPT-4...")
    evaluator.run_evaluation(
        questions_file="evaluation_questions.json",
        embedding_provider="openai",
        llm_model="gpt-4",
        top_k=5,
        output_file="results_openai_gpt4.json"
    )


if __name__ == "__main__":
    main()
