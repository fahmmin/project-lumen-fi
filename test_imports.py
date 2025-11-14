"""
Quick test script to verify all backend imports work correctly
"""

print("Testing PROJECT LUMEN imports...")
print("=" * 60)

try:
    print("✓ Testing backend package...")
    import backend
    print("  SUCCESS: backend package found")
except ImportError as e:
    print(f"  FAILED: {e}")
    exit(1)

try:
    print("✓ Testing backend.config...")
    from backend.config import settings
    print(f"  SUCCESS: App Name = {settings.APP_NAME}")
    print(f"  SUCCESS: Version = {settings.APP_VERSION}")
except ImportError as e:
    print(f"  FAILED: {e}")
    exit(1)

try:
    print("✓ Testing backend.utils.workspace_writer (Windows fcntl fix)...")
    from backend.utils.workspace_writer import workspace, HAS_FCNTL
    print(f"  SUCCESS: Workspace initialized")
    print(f"  INFO: File locking available = {HAS_FCNTL}")
except ImportError as e:
    print(f"  FAILED: {e}")
    exit(1)

try:
    print("✓ Testing backend.routers...")
    from backend.routers import ingest, audit, memory
    print("  SUCCESS: All routers imported")
except ImportError as e:
    print(f"  FAILED: {e}")
    exit(1)

try:
    print("✓ Testing backend.rag components...")
    from backend.rag import vector_store, sparse_retriever
    print("  SUCCESS: RAG components imported")
except ImportError as e:
    print(f"  FAILED: {e}")
    exit(1)

try:
    print("✓ Testing sentence-transformers (huggingface_hub compatibility)...")
    from sentence_transformers import SentenceTransformer
    print("  SUCCESS: sentence-transformers working")
except ImportError as e:
    print(f"  FAILED: {e}")
    exit(1)

try:
    print("✓ Testing FastAPI app initialization...")
    from backend.main import app
    print(f"  SUCCESS: FastAPI app loaded")
    print(f"  App Title: {app.title}")
except Exception as e:
    print(f"  FAILED: {e}")
    exit(1)

print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nYou can now start the server with:")
print("  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
print("\nOr use the run script:")
print("  ./run.bat (Windows)")
print("  ./run.sh (Linux/Mac)")
