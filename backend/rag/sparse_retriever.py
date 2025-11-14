"""
PROJECT LUMEN - Sparse Retrieval (BM25)
BM25-based sparse retrieval using rank_bm25
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict
from rank_bm25 import BM25Okapi
from backend.config import settings
from backend.utils.logger import logger, log_error


class BM25Retriever:
    """BM25-based sparse retrieval"""

    def __init__(self, index_path: Path = settings.BM25_INDEX_PATH):
        self.index_path = index_path
        self.index_path.mkdir(exist_ok=True, parents=True)

        self.bm25 = None
        self.chunks = []
        self.tokenized_corpus = []

        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing BM25 index or create new one"""
        bm25_file = self.index_path / "bm25.pkl"
        chunks_file = self.index_path / "chunks.json"

        if bm25_file.exists() and chunks_file.exists():
            try:
                self._load_index(bm25_file, chunks_file)
                logger.info(f"Loaded BM25 index with {len(self.chunks)} documents")
            except Exception as e:
                log_error(e, "BM25 index loading")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create new BM25 index"""
        self.bm25 = None
        self.chunks = []
        self.tokenized_corpus = []
        logger.info("Created new BM25 index")

    def _load_index(self, bm25_file: Path, chunks_file: Path):
        """Load index from disk"""
        try:
            # Load BM25 index
            with open(bm25_file, 'rb') as f:
                self.bm25 = pickle.load(f)

            # Load chunks
            with open(chunks_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)

            # Recreate tokenized corpus
            self.tokenized_corpus = [self._tokenize(chunk['text']) for chunk in self.chunks]

        except Exception as e:
            log_error(e, "BM25 index loading")
            raise

    def save_index(self):
        """Save index to disk"""
        try:
            bm25_file = self.index_path / "bm25.pkl"
            chunks_file = self.index_path / "chunks.json"

            # Save BM25 index
            with open(bm25_file, 'wb') as f:
                pickle.dump(self.bm25, f)

            # Save chunks
            with open(chunks_file, 'w', encoding='utf-8') as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved BM25 index with {len(self.chunks)} documents")

        except Exception as e:
            log_error(e, "BM25 index saving")
            raise

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        # Simple whitespace tokenization (can be improved with nltk/spacy)
        tokens = text.lower().split()
        # Remove punctuation
        tokens = [''.join(c for c in token if c.isalnum()) for token in tokens]
        # Remove empty tokens
        tokens = [t for t in tokens if t]
        return tokens

    def add_chunks(self, chunks: List[Dict]):
        """
        Add chunks to BM25 index

        Args:
            chunks: List of chunk dictionaries with 'text' field
        """
        if not chunks:
            return

        # Add chunk IDs
        start_id = len(self.chunks)
        for i, chunk in enumerate(chunks):
            chunk['bm25_id'] = start_id + i

        # Store chunks
        self.chunks.extend(chunks)

        # Tokenize new chunks
        new_tokenized = [self._tokenize(chunk['text']) for chunk in chunks]
        self.tokenized_corpus.extend(new_tokenized)

        # Rebuild BM25 index
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        logger.info(f"Added {len(chunks)} chunks to BM25 index (total: {len(self.chunks)})")

    def search(self, query: str, top_k: int = 30) -> List[Dict]:
        """
        Search using BM25

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of chunks with BM25 scores
        """
        if not self.bm25 or not self.chunks:
            logger.warning("BM25 index is empty")
            return []

        # Tokenize query
        tokenized_query = self._tokenize(query)

        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        # Build results
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with positive scores
                chunk = self.chunks[idx].copy()
                chunk['bm25_score'] = float(scores[idx])
                results.append(chunk)

        logger.info(f"BM25 found {len(results)} results")
        return results

    def get_all_chunks(self) -> List[Dict]:
        """Get all chunks"""
        return self.chunks.copy()

    def clear_index(self):
        """Clear the index"""
        self._create_new_index()
        logger.info("BM25 index cleared")


# Global BM25 retriever instance
bm25_retriever = None


def get_bm25_retriever() -> BM25Retriever:
    """Get global BM25 retriever instance"""
    global bm25_retriever
    if bm25_retriever is None:
        bm25_retriever = BM25Retriever()
    return bm25_retriever
