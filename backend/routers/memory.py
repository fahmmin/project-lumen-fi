"""
PROJECT LUMEN - Memory API Router
Handles workspace memory access
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.utils.workspace_writer import workspace
from backend.utils.logger import logger

router = APIRouter(prefix="/memory", tags=["memory"])


class MemoryResponse(BaseModel):
    """Memory response model"""
    workspace_content: str
    last_updated: str
    size_bytes: int


class SearchRequest(BaseModel):
    """Search request model"""
    query: str


@router.get("/", response_model=MemoryResponse)
async def get_workspace_memory():
    """
    Get complete workspace memory

    Returns:
        Full workspace.md content
    """
    try:
        content = workspace.get_content()

        # Get file stats
        import os
        from datetime import datetime

        workspace_path = workspace.workspace_path

        if workspace_path.exists():
            stats = os.stat(workspace_path)
            last_updated = datetime.fromtimestamp(stats.st_mtime).isoformat()
            size_bytes = stats.st_size
        else:
            last_updated = datetime.now().isoformat()
            size_bytes = 0

        return MemoryResponse(
            workspace_content=content,
            last_updated=last_updated,
            size_bytes=size_bytes
        )

    except Exception as e:
        logger.error(f"Error retrieving workspace: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving workspace: {str(e)}"
        )


@router.get("/recent")
async def get_recent_entries(n: int = 10):
    """
    Get recent workspace entries

    Args:
        n: Number of recent entries to retrieve

    Returns:
        Recent entries
    """
    try:
        recent = workspace.get_recent_entries(n=n)

        return {
            "status": "success",
            "entries_count": n,
            "content": recent
        }

    except Exception as e:
        logger.error(f"Error retrieving recent entries: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recent entries: {str(e)}"
        )


@router.post("/search")
async def search_workspace(request: SearchRequest):
    """
    Search workspace for specific entries

    Args:
        request: Search request with query

    Returns:
        Matching entries
    """
    try:
        results = workspace.search_workspace(request.query)

        if results:
            return {
                "status": "success",
                "query": request.query,
                "found": True,
                "content": results
            }
        else:
            return {
                "status": "success",
                "query": request.query,
                "found": False,
                "content": "",
                "message": f"No entries found matching '{request.query}'"
            }

    except Exception as e:
        logger.error(f"Error searching workspace: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching workspace: {str(e)}"
        )


@router.get("/stats")
async def get_workspace_stats():
    """
    Get workspace statistics

    Returns:
        Statistics about workspace
    """
    try:
        content = workspace.get_content()

        # Calculate stats
        lines = content.split('\n')
        total_lines = len(lines)

        # Count sections
        ingestion_count = content.count('### NEW DOCUMENT INGESTED')
        audit_count = content.count('### [AUDIT RUN]')

        # Get file size
        import os
        workspace_path = workspace.workspace_path
        size_bytes = os.stat(workspace_path).st_size if workspace_path.exists() else 0

        return {
            "status": "success",
            "statistics": {
                "total_lines": total_lines,
                "total_characters": len(content),
                "size_bytes": size_bytes,
                "size_kb": round(size_bytes / 1024, 2),
                "documents_ingested": ingestion_count,
                "audits_performed": audit_count
            }
        }

    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating stats: {str(e)}"
        )


@router.delete("/clear")
async def clear_workspace():
    """
    Clear workspace memory (USE WITH CAUTION)

    Returns:
        Confirmation
    """
    try:
        # Backup current workspace
        from datetime import datetime
        import shutil

        workspace_path = workspace.workspace_path
        backup_path = workspace_path.parent / f"workspace_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        if workspace_path.exists():
            shutil.copy(workspace_path, backup_path)

        # Reinitialize workspace
        workspace_path.unlink(missing_ok=True)
        workspace._initialize_workspace()

        logger.warning("Workspace cleared (backup created)")

        return {
            "status": "success",
            "message": "Workspace cleared successfully",
            "backup_file": str(backup_path)
        }

    except Exception as e:
        logger.error(f"Error clearing workspace: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing workspace: {str(e)}"
        )
