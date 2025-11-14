"""
PROJECT LUMEN - Subscriptions API Router
Subscription detection and analysis endpoints
"""

from fastapi import APIRouter, HTTPException

from backend.agents.subscription_agent import get_subscription_agent
from backend.utils.logger import logger

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/{user_id}")
async def get_subscriptions(user_id: str):
    """Get all detected subscriptions"""
    try:
        agent = get_subscription_agent()
        subscriptions = agent.detect_subscriptions(user_id)

        # Calculate summary
        active = [s for s in subscriptions if s.status.value == "active"]
        unused = [s for s in subscriptions if s.status.value == "unused"]

        monthly_cost = sum(s.amount for s in active)
        annual_cost = monthly_cost * 12

        return {
            "user_id": user_id,
            "subscriptions": [s.dict() for s in subscriptions],
            "summary": {
                "total_subscriptions": len(subscriptions),
                "active": len(active),
                "unused": len(unused),
                "monthly_cost": round(monthly_cost, 2),
                "annual_cost": round(annual_cost, 2)
            }
        }
    except Exception as e:
        logger.error(f"Subscriptions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect subscriptions")


@router.get("/{user_id}/unused")
async def get_unused_subscriptions(user_id: str):
    """Get unused subscriptions with savings potential"""
    try:
        agent = get_subscription_agent()
        unused = agent.find_unused_subscriptions(user_id)

        total_savings = sum(s['potential_savings_annual'] for s in unused)

        return {
            "user_id": user_id,
            "unused_subscriptions": unused,
            "total_potential_savings": round(total_savings, 2)
        }
    except Exception as e:
        logger.error(f"Unused subscriptions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to find unused subscriptions")
