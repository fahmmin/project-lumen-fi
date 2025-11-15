"""
Email Integration API - Parse receipts from emails
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from backend.utils.email_parser import email_parser
from backend.rag.chunker import chunk_document
from backend.rag.retriever import index_documents
from backend.routers.ingest import IngestionResponse
from backend.agents.receipt_orchestrator import get_receipt_orchestrator
from backend.utils.logger import logger

router = APIRouter(prefix="/email", tags=["Email Integration"])


class EmailReceiptRequest(BaseModel):
    """Request to parse email receipt"""
    user_id: str
    email_subject: str
    email_body: str
    sender_email: Optional[str] = None


@router.post("/parse-receipt", response_model=IngestionResponse)
async def parse_email_receipt(request: EmailReceiptRequest):
    """
    Parse and upload receipt from email

    **Workflow:**
    1. Extract receipt fields from email text
    2. Create receipt document
    3. Index in vector store
    4. Link to user

    **Usage:**
    ```bash
    curl -X POST "http://localhost:8000/email/parse-receipt" \\
      -H "Content-Type: application/json" \\
      -d '{
        "user_id": "test_user_001",
        "email_subject": "Your Amazon Order Confirmation",
        "email_body": "Thank you for your order...Total: $59.99..."
      }'
    ```

    **Example Email:**
    - Subject: "Your Amazon Order Confirmation"
    - Body: "Total: $59.99...Date: 12/10/2024..."
    """
    try:
        # Parse email
        extracted = email_parser.parse_email(
            email_text=request.email_body,
            subject=request.email_subject
        )

        if extracted.get("confidence", 0) < 0.3:
            raise HTTPException(
                status_code=400,
                detail="Could not extract receipt information from email. Please provide clearer receipt details."
            )

        # Create receipt document
        document_id = f"doc_{uuid.uuid4().hex[:12]}"

        receipt_text = f"""
EMAIL RECEIPT

Subject: {request.email_subject}
From: {request.sender_email or 'Unknown'}

Vendor: {extracted.get('vendor', 'Unknown')}
Date: {extracted.get('date', datetime.now().isoformat())}
Amount: ${extracted.get('amount', 0.0):.2f}
Category: {extracted.get('category', 'general')}

Extracted from email with {extracted.get('confidence', 0) * 100:.0f}% confidence.
        """

        # Index in vector store
        metadata = {
            "document_id": document_id,
            "user_id": request.user_id,
            "vendor": extracted.get('vendor', 'Unknown'),
            "date": extracted.get('date', datetime.now().isoformat()),
            "amount": extracted.get('amount', 0.0),
            "category": extracted.get('category', 'general'),
            "invoice_number": f"EMAIL-{uuid.uuid4().hex[:8].upper()}",
            "source": "email",
            "email_subject": request.email_subject,
            "confidence": extracted.get('confidence', 0)
        }

        chunks = chunk_document(receipt_text, metadata=metadata)
        index_documents(chunks)

        logger.info(f"Email receipt uploaded: {document_id} for user {request.user_id}")

        return IngestionResponse(
            document_id=document_id,
            status="success",
            message=f"Email receipt processed with {extracted.get('confidence', 0) * 100:.0f}% confidence",
            extracted_fields={
                **extracted,
                "source": "email"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing email receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-receipt-smart")
async def parse_receipt_with_intelligence(request: EmailReceiptRequest):
    """
    Parse receipt with complete intelligent analysis using all agents

    **New Enhanced Flow:**
    1. Parse receipt with LLM
    2. Check for duplicates
    3. Real-time budget alerts
    4. Goal impact analysis
    5. Savings opportunities
    6. Pattern detection
    7. Store with enriched metadata

    **Returns:**
    Complete analysis with:
    - Budget alerts
    - Goal impact
    - Savings suggestions
    - Pattern insights
    - Actionable recommendations

    **Usage:**
    ```bash
    curl -X POST "http://localhost:8000/email/parse-receipt-smart" \\
      -H "Content-Type: application/json" \\
      -d '{
        "user_id": "test_user_001",
        "email_subject": "Zomato Order Confirmed",
        "email_body": "Your order from ABC Restaurant...Total: Rs450..."
      }'
    ```
    """
    try:
        # Combine email subject and body for full context
        receipt_text = f"Subject: {request.email_subject}\n\n{request.email_body}"

        # Use orchestrator for complete analysis
        orchestrator = get_receipt_orchestrator()
        result = orchestrator.ingest_receipt(
            receipt_text=receipt_text,
            user_id=request.user_id,
            source="email"
        )

        # Check for failures
        if result['status'] in ['failed', 'duplicate']:
            raise HTTPException(
                status_code=400 if result['status'] == 'duplicate' else 500,
                detail=result.get('message', result.get('error', 'Unknown error'))
            )

        logger.info(f"Smart receipt processing complete for user {request.user_id}")

        return {
            "status": "success",
            "document_id": result.get('receipt', {}).get('document_id'),
            "receipt": result.get('receipt', {}),
            "summary": result.get('summary', ''),
            "alerts": result.get('alerts', []),
            "recommendations": result.get('recommendations', []),
            "detailed_analysis": {
                "budget": result.get('steps', {}).get('budget_alert', {}),
                "goals": result.get('steps', {}).get('goal_impact', {}),
                "savings": result.get('steps', {}).get('savings', {}),
                "patterns": result.get('steps', {}).get('patterns', {})
            },
            "ingested_at": result.get('ingested_at')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in smart receipt processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-parser")
async def test_email_parser(
    email_subject: str = Body(...),
    email_body: str = Body(...)
):
    """
    Test email parser without uploading

    **Returns:**
    Extracted fields and confidence score
    """
    try:
        extracted = email_parser.parse_email(email_body, email_subject)

        return {
            "success": True,
            "extracted_fields": extracted,
            "confidence": extracted.get("confidence", 0),
            "confidence_percentage": f"{extracted.get('confidence', 0) * 100:.0f}%",
            "message": "Parser test successful"
        }

    except Exception as e:
        logger.error(f"Error testing email parser: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/example")
async def get_example_email():
    """
    Get example email for testing

    **Returns:**
    Sample email that the parser can process
    """
    return {
        "example": {
            "email_subject": "Your Amazon Order Confirmation",
            "email_body": """
Thank you for shopping at Amazon

Order Summary:
Date: 12/10/2024
Order #: 123-4567890-1234567

Items:
- Wireless Mouse
- USB Cable
- Laptop Stand

Subtotal: $52.47
Tax: $4.72
Shipping: $2.80

Total: $59.99

Your order will arrive on December 15th.

Thanks,
The Amazon Team
            """,
            "sender_email": "auto-confirm@amazon.com"
        },
        "usage": {
            "endpoint": "POST /email/parse-receipt",
            "note": "Copy the example above and send it to parse-receipt endpoint"
        }
    }
