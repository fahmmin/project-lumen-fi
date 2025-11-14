"""
PROJECT LUMEN - Ingestion API Router
Handles document upload and ingestion
"""

import uuid
import io
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Dict, Optional

from backend.utils.text_extract import extract_text
from backend.utils.llm_parser import parse_document
from backend.rag.chunker import chunk_document
from backend.rag.retriever import index_documents
from backend.utils.workspace_writer import workspace
from backend.config import settings
from backend.utils.logger import logger, log_operation

router = APIRouter(prefix="/ingest", tags=["ingestion"])


class IngestionResponse(BaseModel):
    """Response model for ingestion"""
    status: str
    document_id: str
    filename: str
    user_id: Optional[str] = None
    extracted_fields: Dict
    chunks_created: int
    message: str


@router.post("/", response_model=IngestionResponse)
async def ingest_document(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """
    Ingest a financial document (PDF or image)

    Process:
    1. Validate file
    2. Extract text
    3. Parse into JSON structure
    4. Chunk text
    5. Index in RAG system
    6. Log to workspace.md

    Args:
        file: Uploaded file (PDF or image)
        user_id: Optional user ID to tag receipt (for personal finance features)

    Returns:
        Ingestion response with extracted data
    """
    try:
        # Validate file
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )

        # Check file size
        contents = await file.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )

        logger.info(f"Processing document: {file.filename} ({len(contents)} bytes)")

        # Generate document ID
        document_id = f"doc_{uuid.uuid4().hex[:12]}"

        # Save file
        file_path = settings.UPLOAD_DIR / f"{document_id}{file_ext}"
        with open(file_path, 'wb') as f:
            f.write(contents)

        # Step 1: Extract text
        logger.info("Extracting text from document...")
        file_io = io.BytesIO(contents)
        text = extract_text(file_io, file_extension=file_ext)

        if not text:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract text from document. Please ensure the file is readable."
            )

        logger.info(f"Extracted {len(text)} characters")

        # Step 2: Parse into structured data
        logger.info("Parsing document into structured format...")
        extracted_fields = parse_document(text)

        if not extracted_fields:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse document into structured format"
            )

        # Add document metadata
        extracted_fields['document_id'] = document_id
        extracted_fields['filename'] = file.filename
        extracted_fields['ingestion_timestamp'] = datetime.now().isoformat()

        logger.info(f"Parsed fields: {list(extracted_fields.keys())}")

        # Step 3: Chunk text for RAG
        logger.info("Chunking text for indexing...")
        metadata = {
            "document_id": document_id,
            "filename": file.filename,
            "user_id": user_id if user_id else None,
            "vendor": extracted_fields.get('vendor', ''),
            "date": extracted_fields.get('date', ''),
            "amount": extracted_fields.get('amount', 0),
            "category": extracted_fields.get('category', ''),
            "invoice_number": extracted_fields.get('invoice_number', '')
        }

        chunks = chunk_document(text, metadata=metadata)
        logger.info(f"Created {len(chunks)} chunks")

        # Step 4: Index in RAG system
        logger.info("Indexing chunks in RAG system...")
        index_documents(chunks)
        logger.info("Indexing complete")

        # Step 5: Log to workspace
        logger.info("Logging to workspace...")
        workspace.log_ingestion(
            filename=file.filename,
            extracted_fields=extracted_fields,
            document_id=document_id
        )

        # Log operation
        log_operation("DOCUMENT_INGESTION", {
            "document_id": document_id,
            "filename": file.filename,
            "vendor": extracted_fields.get('vendor', 'Unknown'),
            "amount": extracted_fields.get('amount', 0),
            "chunks": len(chunks)
        })

        return IngestionResponse(
            status="success",
            document_id=document_id,
            filename=file.filename,
            user_id=user_id,
            extracted_fields=extracted_fields,
            chunks_created=len(chunks),
            message=f"Document successfully ingested and indexed ({len(chunks)} chunks created)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during document ingestion: {str(e)}"
        )


@router.get("/status/{document_id}")
async def get_ingestion_status(document_id: str):
    """
    Get ingestion status for a document

    Args:
        document_id: Document ID

    Returns:
        Status information
    """
    try:
        # Check if document exists in workspace
        workspace_content = workspace.get_content()

        if document_id in workspace_content:
            return {
                "status": "ingested",
                "document_id": document_id,
                "message": "Document has been successfully ingested"
            }
        else:
            return {
                "status": "not_found",
                "document_id": document_id,
                "message": "Document not found in system"
            }

    except Exception as e:
        logger.error(f"Error checking ingestion status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking status: {str(e)}"
        )
