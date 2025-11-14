"""
Initialize PROJECT LUMEN with policy documents
This script indexes the policy documents so they're available for RAG retrieval
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import settings
from backend.rag.chunker import chunk_document
from backend.rag.retriever import index_documents
from backend.utils.logger import logger

def initialize_policy_documents():
    """Index all policy documents in the data/policy_docs folder"""

    policy_dir = Path("backend/data/policy_docs")

    if not policy_dir.exists():
        logger.error(f"Policy directory not found: {policy_dir}")
        return False

    # Get all text files in policy_docs
    policy_files = list(policy_dir.glob("*.txt"))

    if not policy_files:
        logger.warning("No policy documents found to index")
        return False

    logger.info(f"Found {len(policy_files)} policy document(s)")

    all_chunks = []

    for policy_file in policy_files:
        logger.info(f"Processing: {policy_file.name}")

        try:
            # Read policy document
            content = policy_file.read_text(encoding='utf-8')

            # Create document metadata
            doc_metadata = {
                "filename": policy_file.name,
                "source": "policy",
                "type": "financial_policy"
            }

            # Chunk the document
            chunks = chunk_document(
                text=content,
                metadata=doc_metadata
            )

            logger.info(f"  Created {len(chunks)} chunks")
            all_chunks.extend(chunks)

        except Exception as e:
            logger.error(f"Error processing {policy_file.name}: {e}")
            continue

    if all_chunks:
        logger.info(f"Indexing {len(all_chunks)} total chunks...")
        try:
            index_documents(all_chunks)
            logger.info("✓ Successfully indexed all policy documents!")
            return True
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            return False
    else:
        logger.warning("No chunks created, nothing to index")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PROJECT LUMEN - Data Initialization")
    print("=" * 60)
    print()

    success = initialize_policy_documents()

    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] Initialization complete!")
        print()
        print("You can now:")
        print("  1. Query the documents via /audit endpoints")
        print("  2. Check /info to see indexed document count")
        print("  3. Upload invoices via /ingest endpoint")
    else:
        print("[FAILED] Initialization failed. Check logs above.")
    print("=" * 60)
