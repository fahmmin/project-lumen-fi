"""
PROJECT LUMEN - Personal Finance API Router
Individual endpoints for finance analysis (no orchestration)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date

from backend.agents.personal_finance_agent import get_personal_finance_agent
from backend.agents.goal_planner_agent import get_goal_planner_agent
from backend.agents.health_score_agent import get_health_score_agent
from backend.agents.behavioral_agent import get_behavioral_agent
from backend.utils.logger import logger

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str, period: str = Query("month", regex="^(month|quarter|year)$")):
    """Get personal finance dashboard"""
    try:
        agent = get_personal_finance_agent()
        return agent.analyze_dashboard(user_id, period)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate dashboard")


@router.get("/spending/{user_id}")
async def get_spending(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None
):
    """Get detailed spending breakdown"""
    try:
        agent = get_personal_finance_agent()

        # Parse dates
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None

        return agent.get_spending_breakdown(user_id, start, end, category)
    except Exception as e:
        logger.error(f"Spending error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get spending data")


@router.get("/predictions/{user_id}")
async def get_predictions(user_id: str):
    """Predict next month's spending"""
    try:
        agent = get_personal_finance_agent()
        return agent.predict_spending(user_id)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate predictions")


@router.get("/budget-recommendations/{user_id}")
async def get_budget_recommendations(user_id: str):
    """Get budget recommendations"""
    try:
        agent = get_personal_finance_agent()
        return agent.get_budget_recommendations(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Budget recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.get("/insights/{user_id}")
async def get_insights(user_id: str):
    """Get AI-powered spending insights"""
    try:
        agent = get_personal_finance_agent()
        dashboard = agent.analyze_dashboard(user_id, "month")

        # Extract insights
        return {
            "user_id": user_id,
            "insights": dashboard.get('insights', [])
        }
    except Exception as e:
        logger.error(f"Insights error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")


@router.get("/health-score/{user_id}")
async def get_health_score(user_id: str):
    """Get financial health score"""
    try:
        agent = get_health_score_agent()
        return agent.calculate_score(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Health score error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate health score")


@router.get("/behavior/{user_id}")
async def get_behavior_analysis(user_id: str):
    """Get behavioral spending analysis"""
    try:
        agent = get_behavioral_agent()
        return agent.analyze_behavior(user_id)
    except Exception as e:
        logger.error(f"Behavioral analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze behavior")


# Goal planning endpoints
@router.get("/{user_id}/goals/{goal_id}/plan")
async def get_goal_plan(user_id: str, goal_id: str):
    """Get savings and investment plan for goal"""
    try:
        agent = get_goal_planner_agent()
        return agent.create_plan(goal_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Goal plan error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create goal plan")


@router.get("/{user_id}/goals/{goal_id}/progress")
async def get_goal_progress(user_id: str, goal_id: str):
    """Track progress toward goal"""
    try:
        agent = get_goal_planner_agent()
        return agent.track_progress(goal_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Goal progress error: {e}")
        raise HTTPException(status_code=500, detail="Failed to track progress")
