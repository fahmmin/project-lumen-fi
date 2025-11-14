"""
Proper initialization script for PROJECT LUMEN
Uses HybridRetriever to correctly index policy documents
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.rag.retriever import get_hybrid_retriever
from backend.rag.chunker import chunk_document
from backend.utils.logger import logger

print("=" * 60)
print("PROJECT LUMEN - Proper Data Initialization")
print("=" * 60)
print()

try:
    # Get the hybrid retriever
    print("Initializing hybrid retriever...")
    retriever = get_hybrid_retriever()
    print(f"  Vector store: {retriever.vector_store.index.ntotal} vectors")
    print(f"  BM25: {len(retriever.bm25.chunks)} documents")

    # Find policy documents
    policy_dir = Path("backend/data/policy_docs")
    policy_files = list(policy_dir.glob("*.txt"))

    if not policy_files:
        print("\n[ERROR] No policy documents found in", policy_dir)
        sys.exit(1)

    print(f"\nFound {len(policy_files)} policy document(s):")
    for pf in policy_files:
        print(f"  - {pf.name}")

    # Process each policy document
    all_chunks = []

    for policy_file in policy_files:
        print(f"\nProcessing: {policy_file.name}")

        # Read content
        content = policy_file.read_text(encoding='utf-8')
        print(f"  File size: {len(content)} characters")

        # Create chunks
        chunks = chunk_document(
            text=content,
            metadata={
                "filename": policy_file.name,
                "source": "policy",
                "type": "financial_policy"
            }
        )

        print(f"  Created: {len(chunks)} chunks")
        all_chunks.extend(chunks)

    print(f"\n{'=' * 60}")
    print(f"Total chunks to index: {len(all_chunks)}")
    print("=" * 60)

    # Add to retriever
    print("\nAdding chunks to retriever...")
    retriever.add_documents(all_chunks)

    print(f"  Vector store now has: {retriever.vector_store.index.ntotal} vectors")
    print(f"  BM25 now has: {len(retriever.bm25.chunks)} documents")

    # Save indices
    print("\nSaving indices...")
    retriever.save_indices()

    print("\n" + "=" * 60)
    print("[SUCCESS] Initialization Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Restart the server to load the new indices")
    print("  2. Check /info endpoint to verify document count")
    print("  3. Test audit API with sample invoice")
    print()
    print("Restart command:")
    print("  ./venv/Scripts/python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
