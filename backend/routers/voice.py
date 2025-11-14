"""
Voice Upload API - Speech-to-Text Receipt Upload
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from pydantic import BaseModel

from backend.utils.voice_processor import voice_processor
from backend.utils.logger import logger
from backend.routers.ingest import IngestionResponse
import uuid
from datetime import datetime

router = APIRouter(prefix="/voice", tags=["Voice Upload"])


class VoiceTranscriptionResponse(BaseModel):
    """Response from voice transcription"""
    success: bool
    transcribed_text: str
    extracted_fields: dict
    method: str
    error: Optional[str] = None


@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (mp3, wav, m4a, ogg, webm)")
):
    """
    Transcribe audio file to text

    **Supported formats:** MP3, WAV, M4A, OGG, WebM

    **Usage:**
    ```bash
    curl -X POST "http://localhost:8000/voice/transcribe" \\
      -F "audio=@recording.mp3"
    ```

    **Returns:**
    - Transcribed text
    - Extracted receipt fields (vendor, amount, date, items)
    - Processing method used
    """
    try:
        # Read audio file
        audio_data = await audio.read()

        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        # Process voice input
        result = await voice_processor.process_voice_input(audio_data, audio.filename)

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to process audio")
            )

        return VoiceTranscriptionResponse(
            success=True,
            transcribed_text=result["transcribed_text"],
            extracted_fields=result["extracted_fields"],
            method=result["method"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-receipt", response_model=IngestionResponse)
async def upload_receipt_by_voice(
    audio: UploadFile = File(..., description="Audio file with receipt details"),
    user_id: str = Form(..., description="User ID")
):
    """
    Upload receipt via voice input

    **Complete workflow:**
    1. Transcribe audio to text
    2. Extract receipt fields (vendor, amount, date, items)
    3. Create receipt document
    4. Index in vector store
    5. Link to user

    **Example voice input:**
    "I spent 59 dollars and 99 cents at Whole Foods on groceries including milk, bread, and vegetables on December 10th"

    **Usage:**
    ```bash
    curl -X POST "http://localhost:8000/voice/upload-receipt" \\
      -F "audio=@receipt_voice.mp3" \\
      -F "user_id=test_user_001"
    ```
    """
    try:
        # Read audio file
        audio_data = await audio.read()

        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        # Transcribe and extract fields
        result = await voice_processor.process_voice_input(audio_data, audio.filename)

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to process audio")
            )

        extracted_fields = result["extracted_fields"]
        transcribed_text = result["transcribed_text"]

        # Create receipt document from extracted fields
        document_id = f"doc_{uuid.uuid4().hex[:12]}"

        # Build receipt text
        receipt_text = f"""
VOICE RECEIPT

Transcribed Input: {transcribed_text}

Vendor: {extracted_fields.get('vendor', 'Unknown')}
Date: {extracted_fields.get('date', datetime.now().isoformat())}
Amount: ${extracted_fields.get('amount', 0.0):.2f}
Category: {extracted_fields.get('category', 'general')}

Items:
{chr(10).join('- ' + item for item in extracted_fields.get('items', ['General purchase']))}
        """

        # Index in vector store
        from backend.rag.chunker import chunk_document
        from backend.rag.retriever import index_documents

        metadata = {
            "document_id": document_id,
            "user_id": user_id,
            "vendor": extracted_fields.get('vendor', 'Unknown'),
            "date": extracted_fields.get('date', datetime.now().isoformat()),
            "amount": extracted_fields.get('amount', 0.0),
            "category": extracted_fields.get('category', 'general'),
            "invoice_number": f"VOICE-{uuid.uuid4().hex[:8].upper()}",
            "source": "voice_input",
            "transcribed_text": transcribed_text
        }

        chunks = chunk_document(receipt_text, metadata=metadata)
        index_documents(chunks)

        logger.info(f"Voice receipt uploaded: {document_id} for user {user_id}")

        return IngestionResponse(
            document_id=document_id,
            status="success",
            message="Voice receipt processed and indexed successfully",
            extracted_fields={
                **extracted_fields,
                "transcribed_text": transcribed_text,
                "source": "voice"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading voice receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported audio formats

    **Returns:**
    List of supported audio file extensions
    """
    return {
        "supported_formats": voice_processor.supported_formats,
        "recommended": [".mp3", ".wav", ".m4a"],
        "note": "Ensure audio is clear with minimal background noise for best results"
    }
