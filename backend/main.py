"""
PROJECT LUMEN - Main FastAPI Application
Entry point for the API server
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend.config import settings
from backend.routers import ingest, audit, memory, users, goals, personal_finance, reminders, subscriptions, forensics, gamification, websocket, voice, family, social, reports, email_integration
from backend.utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-native financial intelligence layer with multimodal analysis and agentic reasoning",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Auto-create user profile middleware
@app.middleware("http")
async def auto_create_user_profile(request: Request, call_next):
    """Auto-create user profile if user_id is in path and profile doesn't exist"""
    from backend.utils.user_storage import get_user_storage
    import re
    
    # Extract user_id from path if present
    path = request.url.path
    
    # Patterns that indicate user_id in path (e.g., /users/profile/{user_id}, /finance/dashboard/{user_id})
    user_id_patterns = [
        r'/users/profile/([^/]+)',
        r'/users/([^/]+)/salary',
        r'/finance/([^/]+)',
        r'/goals/([^/]+)',
        r'/subscriptions/([^/]+)',
        r'/reminders/([^/]+)',
        r'/patterns/([^/]+)',
        r'/gamification/stats/([^/]+)',
        r'/gamification/badges/([^/]+)',
        r'/gamification/daily-login/([^/]+)',
        r'/social/([^/]+)/percentile',
        r'/social/insights/([^/]+)',
        r'/family/user/([^/]+)',
        r'/family/[^/]+/member/([^/]+)',
        r'/reports/generate/([^/]+)',
        r'/reports/([^/]+)/history',
        r'/audit/user/([^/]+)',
        r'/voice/upload-receipt',
        r'/email/parse-receipt',
    ]
    
    user_id = None
    for pattern in user_id_patterns:
        match = re.search(pattern, path)
        if match:
            user_id = match.group(1)
            break
    
    # Also check query params for user_id
    if not user_id:
        user_id = request.query_params.get('user_id')
    
    # Note: We don't read request body here to avoid consuming it
    # Most user_id values should be in path or query params
    # If user_id is in body, the route handler will handle profile creation
    
    # Auto-create profile if user_id found and it looks like a wallet address
    if user_id and (user_id.startswith('0x') or len(user_id) > 20):
        try:
            storage = get_user_storage()
            # This will auto-create if doesn't exist and register in MongoDB
            storage.ensure_profile_exists(user_id.lower())
        except Exception as e:
            # Silently fail - don't block the request
            logger.debug(f"Auto-create profile middleware failed (non-critical): {e}")
    
    response = await call_next(request)
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routers - Phase 1 (Original)
app.include_router(ingest.router)
app.include_router(audit.router)
app.include_router(memory.router)

# Include routers - Phase 2 (Personal Finance)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(personal_finance.router)
app.include_router(reminders.router)
app.include_router(subscriptions.router)
app.include_router(forensics.router)
app.include_router(gamification.router)  # Phase 2: Gamification
app.include_router(websocket.router)  # Phase 2: Real-time alerts
app.include_router(voice.router)  # Phase 2: Voice upload
app.include_router(family.router)  # Phase 2: Family budgets
app.include_router(social.router)  # Phase 2: Social comparison
app.include_router(reports.router)  # Phase 2: PDF reports
app.include_router(email_integration.router)  # Phase 2: Email parsing


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI Financial Intelligence Layer",
        "status": "operational",
        "endpoints": {
            "documentation": "/docs",
            "ingestion": "/ingest",
            "audit": "/audit",
            "memory": "/memory",
            "users": "/users",
            "goals": "/goals",
            "finance": "/finance",
            "reminders": "/reminders",
            "subscriptions": "/subscriptions",
            "forensics": "/forensics",
            "gamification": "/gamification",
            "websocket": "/ws",
            "alerts": "/alerts",
            "voice": "/voice",
            "family": "/family",
            "social": "/social",
            "reports": "/reports",
            "email": "/email"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if critical components are available
        from backend.rag.vector_store import get_vector_store
        from backend.utils.workspace_writer import workspace

        vector_store = get_vector_store()
        workspace_exists = workspace.workspace_path.exists()

        return {
            "status": "healthy",
            "components": {
                "vector_store": {
                    "status": "operational",
                    "documents_indexed": vector_store.index.ntotal if vector_store.index else 0
                },
                "workspace": {
                    "status": "operational" if workspace_exists else "initializing",
                    "path": str(workspace.workspace_path)
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# System info
@app.get("/info")
async def system_info():
    """Get system information"""
    try:
        from backend.rag.vector_store import get_vector_store
        from backend.rag.sparse_retriever import get_bm25_retriever
        import torch

        vector_store = get_vector_store()
        bm25 = get_bm25_retriever()

        return {
            "system": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "debug_mode": settings.DEBUG
            },
            "models": {
                "embedding_model": settings.EMBEDDING_MODEL,
                "reranker_model": settings.RERANKER_MODEL,
                "llm_provider": settings.LLM_PROVIDER,
                "llm_model": settings.LLM_MODEL
            },
            "indices": {
                "vector_store": {
                    "documents": vector_store.index.ntotal if vector_store.index else 0,
                    "dimension": settings.EMBEDDING_DIM
                },
                "bm25": {
                    "documents": len(bm25.chunks)
                }
            },
            "hardware": {
                "cuda_available": torch.cuda.is_available(),
                "device": "cuda" if torch.cuda.is_available() else "cpu"
            },
            "configuration": {
                "chunk_size": settings.CHUNK_SIZE,
                "dense_top_k": settings.DENSE_TOP_K,
                "sparse_top_k": settings.SPARSE_TOP_K,
                "rerank_top_k": settings.RERANK_TOP_K
            }
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)

    try:
        # Initialize workspace
        from backend.utils.workspace_writer import workspace
        logger.info(f"Workspace initialized at: {workspace.workspace_path}")

        # Load models
        from backend.rag.vector_store import get_vector_store
        from backend.rag.sparse_retriever import get_bm25_retriever

        vector_store = get_vector_store()
        logger.info(f"Vector store loaded: {vector_store.index.ntotal} documents")

        bm25 = get_bm25_retriever()
        logger.info(f"BM25 loaded: {len(bm25.chunks)} documents")

        logger.info("=" * 60)
        logger.info("System ready for requests")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down PROJECT LUMEN...")

    try:
        # Save indices
        from backend.rag.vector_store import get_vector_store
        from backend.rag.sparse_retriever import get_bm25_retriever

        vector_store = get_vector_store()
        vector_store.save_index()

        bm25 = get_bm25_retriever()
        bm25.save_index()

        logger.info("Indices saved successfully")
        logger.info("Shutdown complete")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Run with: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
