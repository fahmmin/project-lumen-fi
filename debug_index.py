"""
Debug script to test indexing directly
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.rag.vector_store import get_vector_store
from backend.rag.sparse_retriever import get_bm25_retriever

print("=" * 60)
print("Debug - Direct Index Check")
print("=" * 60)

# Get stores
vector_store = get_vector_store()
bm25 = get_bm25_retriever()

print(f"\nVector Store:")
print(f"  Chunks in memory: {len(vector_store.chunks)}")
print(f"  Vectors in FAISS: {vector_store.index.ntotal}")
print(f"  Chunks file: {vector_store.chunks_path}")
print(f"  Chunks file exists: {vector_store.chunks_path.exists()}")
print(f"  Chunks file size: {vector_store.chunks_path.stat().st_size if vector_store.chunks_path.exists() else 0} bytes")

print(f"\nBM25:")
print(f"  Chunks in memory: {len(bm25.chunks)}")
print(f"  Index path: {bm25.index_path}")

# Try adding a test chunk
print("\n" + "=" * 60)
print("Testing: Adding 1 test chunk...")
print("=" * 60)

test_chunk = {
    "text": "Test policy: All purchases over $1000 require manager approval.",
    "metadata": {"source": "test", "chunk_id": 0}
}

print("\nAdding to vector store...")
vector_store.add_documents([test_chunk])
print(f"  Vectors in FAISS after add: {vector_store.index.ntotal}")
print(f"  Chunks in memory after add: {len(vector_store.chunks)}")

print("\nAdding to BM25...")
bm25.add_documents([test_chunk])
print(f"  BM25 chunks after add: {len(bm25.chunks)}")

print("\nSaving vector store...")
vector_store.save_index()
print(f"  Chunks file size after save: {vector_store.chunks_path.stat().st_size} bytes")

print("\nSaving BM25...")
bm25.save_index()
print(f"  BM25 saved to: {bm25.index_path}")

print("\n" + "=" * 60)
print("Reloading to verify...")
print("=" * 60)

# Reload
from backend.rag.vector_store import VectorStore
from backend.rag.sparse_retriever import BM25Retriever

vs_reload = VectorStore()
bm25_reload = BM25Retriever()

print(f"\nVector Store (reloaded):")
print(f"  Chunks: {len(vs_reload.chunks)}")
print(f"  Vectors: {vs_reload.index.ntotal}")

print(f"\nBM25 (reloaded):")
print(f"  Chunks: {len(bm25_reload.chunks)}")

if len(vs_reload.chunks) > 0:
    print("\n[SUCCESS] Data persisted successfully!")
else:
    print("\n[FAILED] Data did not persist!")

print("=" * 60)
