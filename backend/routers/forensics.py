"""
PROJECT LUMEN - Image Forensics API Router
Image authenticity detection endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import uuid

from backend.agents.forensics_agent import get_forensics_agent
from backend.utils.logger import logger

router = APIRouter(prefix="/forensics", tags=["forensics"])


@router.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze image authenticity

    Upload an image to check for manipulation
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save temporary file
        temp_dir = "backend/data/uploads"
        os.makedirs(temp_dir, exist_ok=True)

        file_ext = os.path.splitext(image.filename)[1]
        temp_filename = f"forensics_{uuid.uuid4().hex[:12]}{file_ext}"
        temp_path = os.path.join(temp_dir, temp_filename)

        # Save uploaded file
        with open(temp_path, "wb") as f:
            content = await image.read()
            f.write(content)

        # Analyze
        agent = get_forensics_agent()
        result = agent.analyze_image(temp_path)

        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass

        return {
            **result,
            "image_file": image.filename
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forensics analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")
