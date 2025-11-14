"""
Gamification API Endpoints - Points, Badges, Streaks, Leaderboards
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from pydantic import BaseModel

from backend.agents.gamification_agent import GamificationAgent
from backend.models.achievement import GamificationStats, LeaderboardEntry
from backend.utils.logger import logger

router = APIRouter(prefix="/gamification", tags=["Gamification"])

# Initialize agent
gamification_agent = GamificationAgent()


class AwardPointsRequest(BaseModel):
    """Request to award points"""
    user_id: str
    activity: str
    metadata: Optional[Dict] = None


@router.post("/points/award", response_model=Dict)
async def award_points(request: AwardPointsRequest):
    """
    Award points to user for an activity

    **Activities:**
    - upload_receipt: 10 points
    - create_goal: 50 points
    - complete_goal: 200 points
    - update_budget: 20 points
    - stay_under_budget: 100 points
    - daily_login: 5 points
    - weekly_streak: 50 points
    - monthly_streak: 200 points
    - share_with_family: 30 points
    - analyze_spending: 15 points
    - save_money: 25 points
    """
    try:
        result = gamification_agent.award_points(
            user_id=request.user_id,
            activity=request.activity,
            metadata=request.metadata
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to award points"))

        return result

    except Exception as e:
        logger.error(f"Error awarding points: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{user_id}", response_model=GamificationStats)
async def get_user_stats(user_id: str):
    """
    Get complete gamification stats for user

    Returns:
    - Total points and level
    - Progress to next level
    - Badges earned/total
    - Current and longest streak
    - Leaderboard rank and percentile
    - Next achievable badges
    """
    try:
        stats = gamification_agent.get_user_stats(user_id)
        return stats

    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Number of top users to return"),
    user_id: Optional[str] = Query(None, description="Current user ID for highlighting")
):
    """
    Get leaderboard of top users

    **Parameters:**
    - limit: Number of users to return (default 10)
    - user_id: Optional current user ID to highlight in leaderboard

    **Returns:**
    Top users ranked by points with anonymized names
    """
    try:
        leaderboard = gamification_agent.get_leaderboard(limit=limit, current_user_id=user_id)
        return leaderboard

    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/badges/{user_id}")
async def get_user_badges(user_id: str):
    """
    Get all badges for user (earned and unearned)

    **Returns:**
    - Earned badges with unlock dates
    - Unearned badges with requirements
    - Total counts
    """
    try:
        badges = gamification_agent.get_user_badges(user_id)
        return badges

    except Exception as e:
        logger.error(f"Error getting user badges: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily-login/{user_id}")
async def record_daily_login(user_id: str):
    """
    Record daily login and update streak

    **Awards:**
    - 5 points for daily login (only once per day)
    - Streak badges if thresholds reached
    """
    try:
        result = gamification_agent.award_points(
            user_id=user_id,
            activity="daily_login"
        )

        # If already logged in today, return success with message
        if not result.get("success") and "already recorded" in result.get("message", ""):
            return {
                "success": True,
                "already_logged_in": True,
                "points_earned": 0,
                "current_streak": result.get("current_streak", 0),
                "total_points": result.get("total_points", 0),
                "message": result.get("message", "Daily login already recorded today")
            }

        return {
            "success": True,
            "already_logged_in": False,
            "points_earned": result.get("points_earned", 0),
            "current_streak": result.get("current_streak", 0),
            "level_up": result.get("level_up", False),
            "badges_unlocked": result.get("badges_unlocked", [])
        }

    except Exception as e:
        logger.error(f"Error recording daily login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
