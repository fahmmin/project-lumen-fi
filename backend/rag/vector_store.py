"""
PROJECT LUMEN - Vector Store
FAISS-based vector storage and retrieval
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer
from backend.config import settings
from backend.utils.logger import logger, log_error


class VectorStore:
    """Manages FAISS vector index and embeddings"""

    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL,
        index_path: Path = settings.VECTOR_INDEX_PATH,
        chunks_path: Path = settings.CHUNKS_FILE
    ):
        self.model_name = model_name
        self.index_path = index_path
        self.chunks_path = chunks_path

        # Load embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # Initialize or load index
        self.index = None
        self.chunks = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if self.index_path.exists() and self.chunks_path.exists():
            try:
                self._load_index()
                logger.info(f"Loaded existing index with {self.index.ntotal} vectors")
            except Exception as e:
                log_error(e, "Index loading")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create new FAISS index"""
        # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.chunks = []
        logger.info(f"Created new FAISS index (dim={self.embedding_dim})")

    def _load_index(self):
        """Load index from disk"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))

            # Load chunks
            with open(self.chunks_path, 'r', encoding='utf-8') as f:
                self.chunks = [json.loads(line) for line in f]

            logger.info(f"Loaded index with {len(self.chunks)} chunks")

        except Exception as e:
            log_error(e, "Index loading")
            raise

    def save_index(self):
        """Save index to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))

            # Save chunks
            with open(self.chunks_path, 'w', encoding='utf-8') as f:
                for chunk in self.chunks:
                    f.write(json.dumps(chunk) + '\n')

            logger.info(f"Saved index with {len(self.chunks)} chunks")

        except Exception as e:
            log_error(e, "Index saving")
            raise

    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts to embeddings

        Args:
            texts: List of texts to encode

        Returns:
            Numpy array of embeddings (normalized)
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        return embeddings

    def add_chunks(self, chunks: List[Dict]):
        """
        Add chunks to the index

        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
        """
        if not chunks:
            return

        # Extract texts
        texts = [chunk['text'] for chunk in chunks]

        # Generate embeddings
        logger.info(f"Encoding {len(texts)} chunks...")
        embeddings = self.encode_texts(texts)

        # Add to FAISS index
        self.index.add(embeddings)

        # Add chunk IDs
        start_id = len(self.chunks)
        for i, chunk in enumerate(chunks):
            chunk['id'] = start_id + i

        # Store chunks
        self.chunks.extend(chunks)

        logger.info(f"Added {len(chunks)} chunks to index (total: {self.index.ntotal})")

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search for similar chunks

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of chunk dictionaries with scores
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty")
            return []

        # Encode query
        query_embedding = self.encode_texts([query])

        # Search
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        # Get results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk['score'] = float(score)
                results.append(chunk)

        logger.info(f"Found {len(results)} results for query")
        return results

    def search_by_embedding(self, embedding: np.ndarray, top_k: int = 10) -> List[Dict]:
        """
        Search using pre-computed embedding

        Args:
            embedding: Query embedding (normalized)
            top_k: Number of results

        Returns:
            List of chunks with scores
        """
        if self.index.ntotal == 0:
            return []

        # Ensure embedding is 2D
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)

        # Normalize
        faiss.normalize_L2(embedding)

        # Search
        scores, indices = self.index.search(embedding, min(top_k, self.index.ntotal))

        # Get results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk['score'] = float(score)
                results.append(chunk)

        return results

    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict]:
        """
        Get chunk by ID

        Args:
            chunk_id: Chunk ID

        Returns:
            Chunk dictionary or None
        """
        for chunk in self.chunks:
            if chunk.get('id') == chunk_id:
                return chunk
        return None

    def get_all_chunks(self) -> List[Dict]:
        """Get all chunks"""
        return self.chunks.copy()

    def clear_index(self):
        """Clear the index"""
        self._create_new_index()
        logger.info("Index cleared")


# Global vector store instance
vector_store = None


def get_vector_store() -> VectorStore:
    """Get global vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store
