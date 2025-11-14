"""
Social Comparison API - Anonymous spending comparisons
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.agents.social_comparison_agent import social_comparison_agent
from backend.utils.logger import logger

router = APIRouter(prefix="/social", tags=["Social Comparison"])


@router.get("/{user_id}/percentile")
async def get_user_percentile(
    user_id: str,
    period: str = Query("month", enum=["month", "quarter", "year"])
):
    """
    Get user's spending percentile compared to all users

    **Returns:**
    - Overall spending percentile (0-100)
    - Rank among all users
    - Category-specific percentiles
    - Comparison to average
    - Anonymous insights

    **Example:**
    - 75th percentile = You spend more than 75% of users
    - 25th percentile = You spend less than 75% of users
    """
    try:
        comparison = social_comparison_agent.get_user_percentile(user_id, period)

        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user percentile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category}/leaderboard")
async def get_category_leaderboard(
    category: str,
    period: str = Query("month", enum=["month", "quarter", "year"]),
    limit: int = Query(10, ge=1, le=50, description="Number of top users")
):
    """
    Get top spenders in a category (anonymized)

    **Returns:**
    - Top N users in category (anonymized)
    - Average spending in category
    - Category statistics

    **Categories:**
    groceries, dining, transportation, entertainment, shopping, healthcare, etc.
    """
    try:
        leaderboard = social_comparison_agent.get_category_leaderboard(
            category=category,
            period=period,
            limit=limit
        )

        return leaderboard

    except Exception as e:
        logger.error(f"Error getting category leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{user_id}")
async def get_social_insights(
    user_id: str,
    period: str = Query("month", enum=["month", "quarter", "year"])
):
    """
    Get personalized insights based on social comparison

    **Returns:**
    - How user compares to others
    - Categories where user excels or overspends
    - Behavioral nudges based on peer comparison
    """
    try:
        comparison = social_comparison_agent.get_user_percentile(user_id, period)

        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])

        # Extract just the insights
        return {
            "user_id": user_id,
            "period": period,
            "insights": comparison.get("insights", []),
            "overall_status": comparison["overall"]["status"],
            "percentile": comparison["overall"]["percentile"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting social insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
