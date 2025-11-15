"""
PROJECT LUMEN - Audit API Router
Handles audit execution
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, model_validator, Field
from typing import Dict, List, Optional, Any

from backend.agents.orchestrator import run_audit, get_orchestrator
from backend.utils.logger import logger

router = APIRouter(prefix="/audit", tags=["audit"])


class InvoiceData(BaseModel):
    """
    Invoice data model - all fields from LLM parsing
    Note: Some fields have defaults to be more lenient with frontend requests
    """
    vendor: str
    date: str
    amount: float
    tax: float = 0.0  # Default to 0.0 if not provided
    category: str = "general"  # Default category if not provided
    invoice_number: str = ""  # Default to empty string if not provided
    items: List[Dict] = Field(default_factory=list)  # May be empty if no line items
    payment_method: Optional[str] = None  # Optional field

    @model_validator(mode='before')
    @classmethod
    def validate_and_set_defaults(cls, data: Any) -> Any:
        """Convert empty strings and None to defaults before validation"""
        if isinstance(data, dict):
            # Handle category
            if 'category' in data:
                if data['category'] == '' or data['category'] is None:
                    data['category'] = "general"
            else:
                data['category'] = "general"
            
            # Handle tax
            if 'tax' in data:
                if data['tax'] is None:
                    data['tax'] = 0.0
            else:
                data['tax'] = 0.0
            
            # Handle invoice_number
            if 'invoice_number' in data:
                if data['invoice_number'] is None:
                    data['invoice_number'] = ""
            else:
                data['invoice_number'] = ""
            
            # Handle items - ensure it's a list
            if 'items' not in data:
                data['items'] = []
            elif data['items'] is None:
                data['items'] = []
        
        return data


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
async def execute_audit(request: AuditRequest, user_id: Optional[str] = Query(None)):
    """
    Execute comprehensive audit on invoice

    Process:
    1. Run Audit Agent (duplicates, patterns, totals)
    2. Run Compliance Agent (policy validation via RAG)
    3. Run Fraud Agent (anomaly detection)
    4. Run Explainability Agent (generate summary)
    5. Log to workspace.md
    6. Save to MongoDB (silently, no frontend indication)

    Args:
        request: Audit request with invoice data
        user_id: Optional user ID for MongoDB storage

    Returns:
        Complete audit report
    """
    try:
        logger.info(f"Audit request received for vendor: {request.invoice_data.vendor}")
        logger.debug(f"Audit request data: vendor={request.invoice_data.vendor}, amount={request.invoice_data.amount}, category={request.invoice_data.category}")

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

        # Save to MongoDB (silently, don't expose to frontend)
        try:
            from backend.utils.mongo_storage import get_mongo_storage
            mongo_storage = get_mongo_storage()
            amount = invoice_dict.get('amount', 0.0)
            mongo_storage.save_audit(
                audit_id=audit_report['audit_id'],
                audit_report=audit_report,
                amount=amount,
                user_id=user_id
            )
        except Exception as mongo_error:
            # Silently fail - MongoDB is optional
            logger.debug(f"MongoDB save failed (non-critical): {mongo_error}")

        return AuditResponse(**audit_report)

    except Exception as e:
        logger.error(f"Error during audit execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during audit: {str(e)}"
        )


@router.post("/quick")
async def quick_audit(invoice_data: InvoiceData, user_id: Optional[str] = Query(None)):
    """
    Quick audit using only Audit Agent (no RAG, no LLM)

    Args:
        invoice_data: Invoice data
        user_id: Optional user ID for MongoDB storage

    Returns:
        Quick audit results
    """
    try:
        from backend.agents.audit_agent import get_audit_agent
        import uuid
        from datetime import datetime

        logger.info("Quick audit requested")

        invoice_dict = invoice_data.dict()
        audit_agent = get_audit_agent()

        findings = audit_agent.audit(invoice_dict)

        # Create a minimal audit report for MongoDB storage
        audit_id = f"audit_{uuid.uuid4().hex[:8]}"
        audit_report = {
            "audit_id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "invoice_data": invoice_dict,
            "findings": {"audit": findings},
            "explanation": "",
            "context_chunks": [],
            "overall_status": findings.get("status", "pass")
        }

        # Save to MongoDB (silently, don't expose to frontend)
        try:
            from backend.utils.mongo_storage import get_mongo_storage
            mongo_storage = get_mongo_storage()
            amount = invoice_dict.get('amount', 0.0)
            mongo_storage.save_audit(
                audit_id=audit_id,
                audit_report=audit_report,
                amount=amount,
                user_id=user_id
            )
        except Exception as mongo_error:
            # Silently fail - MongoDB is optional
            logger.debug(f"MongoDB save failed (non-critical): {mongo_error}")

        return {
            "status": "success",
            "audit_type": "quick",
            "audit_id": audit_id,
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
        # Try MongoDB first
        from backend.utils.mongo_storage import get_mongo_storage
        mongo_storage = get_mongo_storage()
        if mongo_storage.is_connected():
            audit_doc = mongo_storage.get_audit(audit_id)
            if audit_doc:
                return {
                    "status": "found",
                    "audit_id": audit_id,
                    "audit_report": audit_doc.get("audit_report", {}),
                    "amount": audit_doc.get("amount", 0),
                    "timestamp": audit_doc.get("timestamp", "").isoformat() if hasattr(audit_doc.get("timestamp", ""), "isoformat") else str(audit_doc.get("timestamp", ""))
                }
        
        # Fallback to workspace
        from backend.utils.workspace_writer import workspace
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


@router.get("/user/{user_id}/audits")
async def get_user_audits(user_id: str, limit: int = 100):
    """
    Get all audits for a user from MongoDB
    
    Args:
        user_id: User ID
        limit: Maximum number of audits to return
        
    Returns:
        List of user audits
    """
    try:
        from backend.utils.mongo_storage import get_mongo_storage
        mongo_storage = get_mongo_storage()
        
        if not mongo_storage.is_connected():
            return {
                "status": "success",
                "audits": [],
                "count": 0,
                "message": "MongoDB not connected"
            }
        
        audits = mongo_storage.get_user_audits(user_id, limit)
        
        return {
            "status": "success",
            "audits": audits,
            "count": len(audits)
        }
    except Exception as e:
        logger.error(f"Error getting user audits: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user audits: {str(e)}"
        )


@router.get("/user/{user_id}/stats")
async def get_user_audit_stats(user_id: str):
    """
    Get audit statistics for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Audit statistics
    """
    try:
        from backend.utils.mongo_storage import get_mongo_storage
        mongo_storage = get_mongo_storage()
        
        if not mongo_storage.is_connected():
            return {
                "total_audits": 0,
                "total_amount": 0,
                "by_status": {},
                "by_category": {},
                "recent_count": 0
            }
        
        stats = mongo_storage.get_audit_stats(user_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting user audit stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving audit stats: {str(e)}"
        )
