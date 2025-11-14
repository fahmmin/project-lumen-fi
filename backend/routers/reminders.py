"""
PROJECT LUMEN - Reminders & Patterns API Router
Smart reminders and pattern detection endpoints
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from backend.agents.pattern_agent import get_pattern_agent
from backend.utils.logger import logger

router = APIRouter(tags=["reminders"])


@router.get("/reminders/{user_id}")
async def get_reminders(user_id: str):
    """Get active smart reminders"""
    try:
        agent = get_pattern_agent()
        reminders = agent.generate_reminders(user_id)

        return {
            "user_id": user_id,
            "reminders": [r.dict() for r in reminders],
            "total_reminders": len(reminders)
        }
    except Exception as e:
        logger.error(f"Reminders error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate reminders")


@router.get("/patterns/{user_id}")
async def get_patterns(user_id: str):
    """Get detected spending patterns"""
    try:
        agent = get_pattern_agent()
        patterns = agent.detect_patterns(user_id)

        return {
            "user_id": user_id,
            "patterns": [p.dict() for p in patterns],
            "total_patterns": len(patterns)
        }
    except Exception as e:
        logger.error(f"Patterns error: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect patterns")
