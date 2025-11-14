"""
PROJECT LUMEN - Reranker
MonoT5-based reranking for hybrid retrieval
"""

from typing import List, Dict
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from backend.config import settings
from backend.utils.logger import logger, log_error


class MonoT5Reranker:
    """MonoT5-based reranker for passages"""

    def __init__(self, model_name: str = settings.RERANKER_MODEL):
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        logger.info(f"Loading reranker model: {model_name} on {self.device}")

        try:
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Reranker model loaded successfully")
        except Exception as e:
            log_error(e, "Reranker model loading")
            self.tokenizer = None
            self.model = None

    def rerank(self, query: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Rerank chunks using MonoT5 model - requires model to be loaded

        Args:
            query: Search query
            chunks: List of chunk dictionaries with 'text' field
            top_k: Number of top results to return

        Returns:
            Reranked chunks with relevance scores

        Raises:
            RuntimeError: If reranker model is not loaded
        """
        if not chunks:
            return []

        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Reranker model not loaded. Cannot perform reranking without MonoT5 model.")

        # Prepare inputs
        pairs = [(query, chunk['text']) for chunk in chunks]
        scores = self._score_pairs(pairs)

        # Add scores to chunks
        for chunk, score in zip(chunks, scores):
            chunk['rerank_score'] = score

        # Sort by rerank score
        reranked = sorted(chunks, key=lambda x: x['rerank_score'], reverse=True)

        logger.info(f"Reranked {len(chunks)} chunks with MonoT5, returning top {top_k}")
        return reranked[:top_k]

    def _score_pairs(self, pairs: List[tuple]) -> List[float]:
        """
        Score query-document pairs

        Args:
            pairs: List of (query, document) tuples

        Returns:
            List of relevance scores
        """
        scores = []

        # Process in batches to avoid memory issues
        batch_size = 8
        for i in range(0, len(pairs), batch_size):
            batch_pairs = pairs[i:i + batch_size]
            batch_scores = self._score_batch(batch_pairs)
            scores.extend(batch_scores)

        return scores

    def _score_batch(self, pairs: List[tuple]) -> List[float]:
        """
        Score a batch of pairs

        Args:
            pairs: List of (query, document) tuples

        Returns:
            List of scores
        """
        # Format inputs for MonoT5: "Query: {query} Document: {document} Relevant:"
        inputs = [f"Query: {query} Document: {doc} Relevant:" for query, doc in pairs]

        # Tokenize
        encoded = self.tokenizer(
            inputs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors='pt'
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **encoded,
                max_new_tokens=2,
                return_dict_in_generate=True,
                output_scores=True
            )

        # Get logits for 'true' token
        # MonoT5 generates 'true' or 'false' for relevance
        logits = outputs.scores[0]  # First token logits
        true_token_id = self.tokenizer.encode('true')[0]
        false_token_id = self.tokenizer.encode('false')[0]

        # Extract scores (logit for 'true')
        scores = []
        for i in range(len(pairs)):
            true_score = logits[i, true_token_id].item()
            false_score = logits[i, false_token_id].item()

            # Normalize to probability-like score
            score = torch.softmax(torch.tensor([false_score, true_score]), dim=0)[1].item()
            scores.append(score)

        return scores


# Global reranker instance
reranker = None


def get_reranker() -> MonoT5Reranker:
    """Get global reranker instance"""
    global reranker
    if reranker is None:
        reranker = MonoT5Reranker()
    return reranker


def rerank_chunks(query: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
    """
    Rerank chunks

    Args:
        query: Search query
        chunks: List of chunks
        top_k: Number of results

    Returns:
        Reranked chunks
    """
    ranker = get_reranker()
    return ranker.rerank(query, chunks, top_k)
