"""
PROJECT LUMEN - Hybrid Retriever
Orchestrates dense + sparse + HyDE + reranking
"""

from typing import List, Dict, Set
from backend.rag.vector_store import get_vector_store
from backend.rag.sparse_retriever import get_bm25_retriever
from backend.rag.hyde import generate_hyde
from backend.rag.reranker import get_reranker
from backend.config import settings
from backend.utils.logger import logger


class HybridRetriever:
    """
    Hybrid retrieval combining:
    1. HyDE for query enhancement
    2. Dense retrieval (FAISS)
    3. Sparse retrieval (BM25)
    4. Reranking (MonoT5)
    """

    def __init__(
        self,
        dense_top_k: int = settings.DENSE_TOP_K,
        sparse_top_k: int = settings.SPARSE_TOP_K,
        final_top_k: int = settings.RERANK_TOP_K,
        use_hyde: bool = True
    ):
        self.dense_top_k = dense_top_k
        self.sparse_top_k = sparse_top_k
        self.final_top_k = final_top_k
        self.use_hyde = use_hyde

        # Initialize retrievers
        self.vector_store = get_vector_store()
        self.bm25 = get_bm25_retriever()
        self.reranker = get_reranker()

    def retrieve(self, query: str, use_hyde: bool = None) -> List[Dict]:
        """
        Perform hybrid retrieval

        Steps:
        1. Generate HyDE document (optional)
        2. Dense retrieval using HyDE or original query
        3. Sparse retrieval using original query
        4. Merge and deduplicate
        5. Rerank with MonoT5
        6. Return top-k

        Args:
            query: Search query
            use_hyde: Override HyDE usage

        Returns:
            List of top-k reranked chunks
        """
        logger.info(f"Starting hybrid retrieval for query: {query[:100]}...")

        # Determine if using HyDE
        use_hyde_flag = use_hyde if use_hyde is not None else self.use_hyde

        # Step 1: HyDE generation (optional)
        search_query = query
        if use_hyde_flag:
            hyde_doc = generate_hyde(query)
            if hyde_doc and hyde_doc != query:
                search_query = hyde_doc
                logger.info("Using HyDE-enhanced query for dense retrieval")

        # Step 2: Dense retrieval
        dense_results = self.vector_store.search(search_query, top_k=self.dense_top_k)
        logger.info(f"Dense retrieval: {len(dense_results)} results")

        # Step 3: Sparse retrieval (always use original query)
        sparse_results = self.bm25.search(query, top_k=self.sparse_top_k)
        logger.info(f"Sparse retrieval: {len(sparse_results)} results")

        # Step 4: Merge and deduplicate
        merged_results = self._merge_results(dense_results, sparse_results)
        logger.info(f"Merged: {len(merged_results)} unique results")

        # Step 5: Rerank
        if merged_results:
            reranked_results = self.reranker.rerank(
                query,  # Use original query for reranking
                merged_results,
                top_k=self.final_top_k
            )
            logger.info(f"Reranked: returning top {len(reranked_results)} results")
            return reranked_results
        else:
            logger.warning("No results to rerank")
            return []

    def _merge_results(self, dense_results: List[Dict], sparse_results: List[Dict]) -> List[Dict]:
        """
        Merge dense and sparse results, removing duplicates

        Args:
            dense_results: Results from dense retrieval
            sparse_results: Results from sparse retrieval

        Returns:
            Merged unique results
        """
        # Use chunk text as unique identifier
        seen_texts: Set[str] = set()
        merged = []

        # Add dense results first (usually higher quality)
        for chunk in dense_results:
            text = chunk['text']
            if text not in seen_texts:
                seen_texts.add(text)
                # Normalize score for merging
                chunk['retrieval_score'] = chunk.get('score', 0.0)
                merged.append(chunk)

        # Add sparse results
        for chunk in sparse_results:
            text = chunk['text']
            if text not in seen_texts:
                seen_texts.add(text)
                # Normalize BM25 score (scale to 0-1 range approximately)
                bm25_score = chunk.get('bm25_score', 0.0)
                chunk['retrieval_score'] = min(bm25_score / 10.0, 1.0)
                merged.append(chunk)

        return merged

    def retrieve_simple(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Simple retrieval using only dense search (no HyDE, no reranking)

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            Top-k results
        """
        return self.vector_store.search(query, top_k=top_k)

    def add_documents(self, chunks: List[Dict]):
        """
        Add documents to both dense and sparse indices

        Args:
            chunks: List of chunk dictionaries
        """
        if not chunks:
            return

        logger.info(f"Adding {len(chunks)} chunks to retrieval indices...")

        # Add to vector store
        self.vector_store.add_chunks(chunks)

        # Add to BM25
        self.bm25.add_chunks(chunks)

        logger.info("Chunks added to all indices")

    def save_indices(self):
        """Save all indices to disk"""
        logger.info("Saving retrieval indices...")
        self.vector_store.save_index()
        self.bm25.save_index()
        logger.info("Indices saved successfully")


# Global hybrid retriever instance
hybrid_retriever = None


def get_hybrid_retriever() -> HybridRetriever:
    """Get global hybrid retriever instance"""
    global hybrid_retriever
    if hybrid_retriever is None:
        hybrid_retriever = HybridRetriever()
    return hybrid_retriever


def search(query: str, top_k: int = 5, use_hyde: bool = True) -> List[Dict]:
    """
    Perform hybrid search

    Args:
        query: Search query
        top_k: Number of results
        use_hyde: Whether to use HyDE

    Returns:
        Top-k chunks
    """
    retriever = get_hybrid_retriever()
    retriever.final_top_k = top_k
    return retriever.retrieve(query, use_hyde=use_hyde)


def index_documents(chunks: List[Dict]):
    """
    Index documents for retrieval

    Args:
        chunks: List of chunks to index
    """
    retriever = get_hybrid_retriever()
    retriever.add_documents(chunks)
    retriever.save_indices()
