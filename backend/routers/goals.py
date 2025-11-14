"""
PROJECT LUMEN - Goals Management API Router
Handles financial goal creation, tracking, and management
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.models.goal import FinancialGoal, GoalCreate, GoalUpdate
from backend.utils.user_storage import get_user_storage
from backend.utils.logger import logger

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_goal(goal_data: GoalCreate):
    """
    Create a new financial goal

    Args:
        goal_data: Goal creation data

    Returns:
        Success message with goal_id

    Raises:
        404: User not found
        500: Internal error
    """
    try:
        storage = get_user_storage()
        goal = storage.create_goal(goal_data)

        return {
            "status": "success",
            "message": "Goal created successfully",
            "goal_id": goal.goal_id,
            "name": goal.name,
            "created_at": goal.created_at.isoformat()
        }

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating goal: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create goal: {str(e)}"
        )


@router.get("/{user_id}", response_model=dict)
async def list_user_goals(user_id: str):
    """
    List all goals for a user

    Args:
        user_id: User ID

    Returns:
        List of goals
    """
    storage = get_user_storage()
    goals = storage.list_goals(user_id)

    return {
        "user_id": user_id,
        "goals": [goal.dict() for goal in goals],
        "total_goals": len(goals)
    }


@router.get("/{user_id}/{goal_id}", response_model=FinancialGoal)
async def get_goal(user_id: str, goal_id: str):
    """
    Get specific goal details

    Args:
        user_id: User ID
        goal_id: Goal ID

    Returns:
        Goal details

    Raises:
        404: Goal not found
    """
    storage = get_user_storage()
    goal = storage.get_goal(goal_id, user_id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found for user {user_id}"
        )

    return goal


@router.put("/{goal_id}", response_model=FinancialGoal)
async def update_goal(goal_id: str, user_id: str, update_data: GoalUpdate):
    """
    Update a goal

    Args:
        goal_id: Goal ID
        user_id: User ID (query parameter)
        update_data: Update data

    Returns:
        Updated goal

    Raises:
        404: Goal not found
    """
    try:
        storage = get_user_storage()
        goal = storage.update_goal(goal_id, user_id, update_data)
        return goal

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{goal_id}", response_model=dict)
async def delete_goal(goal_id: str, user_id: str):
    """
    Delete a goal

    Args:
        goal_id: Goal ID
        user_id: User ID (query parameter)

    Returns:
        Success message

    Raises:
        404: Goal not found
    """
    try:
        storage = get_user_storage()
        storage.delete_goal(goal_id, user_id)

        return {
            "status": "success",
            "message": f"Goal {goal_id} deleted successfully"
        }

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
