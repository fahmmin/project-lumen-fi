"""
PROJECT LUMEN - Audit API Router
Handles audit execution
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

from backend.agents.orchestrator import run_audit, get_orchestrator
from backend.utils.logger import logger

router = APIRouter(prefix="/audit", tags=["audit"])


class InvoiceData(BaseModel):
    """
    Invoice data model - all fields from LLM parsing
    Note: LLM parser requires all fields to be present, no defaults used
    """
    vendor: str
    date: str
    amount: float
    tax: float  # LLM must provide, or 0.0 if not found
    category: str  # LLM must provide category, no "Uncategorized" fallback
    invoice_number: str  # LLM must provide invoice number or identifier
    items: Optional[List[Dict]] = []  # May be empty if no line items
    payment_method: Optional[str] = None  # Optional field


class AuditRequest(BaseModel):
    """Audit request model"""
    invoice_data: InvoiceData
    agents: Optional[List[str]] = None  # If None, run all agents


class AuditResponse(BaseModel):
    """Audit response model"""
    audit_id: str
    timestamp: str
    invoice_data: Dict
    findings: Dict
    explanation: Optional[str] = ""
    context_chunks: List
    overall_status: str


@router.post("/", response_model=AuditResponse)
async def execute_audit(request: AuditRequest):
    """
    Execute comprehensive audit on invoice

    Process:
    1. Run Audit Agent (duplicates, patterns, totals)
    2. Run Compliance Agent (policy validation via RAG)
    3. Run Fraud Agent (anomaly detection)
    4. Run Explainability Agent (generate summary)
    5. Log to workspace.md

    Args:
        request: Audit request with invoice data

    Returns:
        Complete audit report
    """
    try:
        logger.info(f"Audit request received for vendor: {request.invoice_data.vendor}")

        # Convert Pydantic model to dict
        invoice_dict = request.invoice_data.dict()

        # Run audit
        if request.agents:
            # Partial audit with selected agents
            orchestrator = get_orchestrator()
            audit_report = orchestrator.run_partial_audit(invoice_dict, request.agents)
        else:
            # Full audit with all agents
            audit_report = run_audit(invoice_dict)

        logger.info(f"Audit completed: {audit_report['audit_id']} - Status: {audit_report['overall_status']}")

        return AuditResponse(**audit_report)

    except Exception as e:
        logger.error(f"Error during audit execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during audit: {str(e)}"
        )


@router.post("/quick")
async def quick_audit(invoice_data: InvoiceData):
    """
    Quick audit using only Audit Agent (no RAG, no LLM)

    Args:
        invoice_data: Invoice data

    Returns:
        Quick audit results
    """
    try:
        from backend.agents.audit_agent import get_audit_agent

        logger.info("Quick audit requested")

        invoice_dict = invoice_data.dict()
        audit_agent = get_audit_agent()

        findings = audit_agent.audit(invoice_dict)

        return {
            "status": "success",
            "audit_type": "quick",
            "findings": findings,
            "message": "Quick audit completed (Audit Agent only)"
        }

    except Exception as e:
        logger.error(f"Error during quick audit: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during quick audit: {str(e)}"
        )


@router.get("/history")
async def get_audit_history(limit: int = 10):
    """
    Get recent audit history from workspace

    Args:
        limit: Number of recent audits to return

    Returns:
        Recent audit entries
    """
    try:
        from backend.utils.workspace_writer import workspace

        recent_entries = workspace.get_recent_entries(n=limit)

        return {
            "status": "success",
            "entries_count": limit,
            "content": recent_entries
        }

    except Exception as e:
        logger.error(f"Error retrieving audit history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@router.get("/{audit_id}")
async def get_audit_by_id(audit_id: str):
    """
    Retrieve specific audit by ID

    Args:
        audit_id: Audit ID

    Returns:
        Audit details
    """
    try:
        from backend.utils.workspace_writer import workspace

        # Search workspace for audit
        audit_content = workspace.search_workspace(audit_id)

        if audit_content:
            return {
                "status": "found",
                "audit_id": audit_id,
                "content": audit_content
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Audit {audit_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving audit: {str(e)}"
        )
