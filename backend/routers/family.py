"""
Family/Shared Budgets API - Invite-based family groups
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from backend.models.family import (
    Family, FamilyCreate, FamilyJoin, FamilyUpdate, FamilyDashboard
)
from backend.utils.family_storage import family_storage
from backend.agents.family_analytics_agent import family_analytics_agent
from backend.utils.logger import logger

router = APIRouter(prefix="/family", tags=["Family & Shared Budgets"])


@router.post("/create", response_model=Family)
async def create_family(family_data: FamilyCreate):
    """
    Create a new family/household group

    **Creates:**
    - New family with unique 6-character invite code
    - Creator becomes admin
    - Optional shared budget

    **Returns:**
    - Family details with invite code to share with family members
    """
    try:
        family = family_storage.create_family(family_data)
        return family

    except Exception as e:
        logger.error(f"Error creating family: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/join", response_model=Family)
async def join_family(join_data: FamilyJoin):
    """
    Join an existing family using invite code

    **Required:**
    - 6-character invite code (case-insensitive)
    - User ID
    - Optional display name

    **Returns:**
    - Updated family with new member
    """
    try:
        family = family_storage.join_family(
            invite_code=join_data.invite_code.upper(),
            user_id=join_data.user_id,
            display_name=join_data.display_name
        )
        return family

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error joining family: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{family_id}", response_model=Family)
async def get_family(family_id: str):
    """
    Get family details

    **Returns:**
    - Family information
    - Member list
    - Shared budget
    - Invite code
    """
    try:
        family = family_storage.get_family_by_id(family_id)

        if not family:
            raise HTTPException(status_code=404, detail="Family not found")

        return family

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting family: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/families", response_model=List[Family])
async def get_user_families(user_id: str):
    """
    Get all families a user belongs to

    **Returns:**
    List of families the user is a member of
    """
    try:
        families = family_storage.get_user_families(user_id)
        return families

    except Exception as e:
        logger.error(f"Error getting user families: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{family_id}/dashboard")
async def get_family_dashboard(
    family_id: str,
    period: str = Query("month", enum=["month", "quarter", "year"], description="Time period for analysis")
):
    """
    Get aggregated family financial dashboard

    **Returns:**
    - Total family spending
    - Spending by member
    - Spending by category
    - Shared budget status
    - Top spenders
    - Family insights
    """
    try:
        dashboard = family_analytics_agent.get_family_dashboard(family_id, period)
        return dashboard

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting family dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{family_id}/member/{user_id}/comparison")
async def get_member_comparison(
    family_id: str,
    user_id: str,
    period: str = Query("month", enum=["month", "quarter", "year"])
):
    """
    Compare member's spending to family averages

    **Returns:**
    - User's spending vs family average
    - Category-by-category comparison
    - Rank within family
    - Personalized insights
    """
    try:
        comparison = family_analytics_agent.get_member_comparison(family_id, user_id, period)
        return comparison

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting member comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{family_id}/update", response_model=Family)
async def update_family(
    family_id: str,
    user_id: str = Query(..., description="User ID (must be admin)"),
    updates: FamilyUpdate = ...
):
    """
    Update family settings (admin only)

    **Can update:**
    - Family name
    - Description
    - Shared budget

    **Requires:**
    - User must be family admin
    """
    try:
        family = family_storage.update_family(family_id, user_id, updates)
        return family

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating family: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{family_id}/leave")
async def leave_family(
    family_id: str,
    user_id: str = Query(..., description="User ID")
):
    """
    Leave a family

    **Notes:**
    - Admin cannot leave if other members exist
    - If last member leaves, family is deleted
    """
    try:
        success = family_storage.leave_family(family_id, user_id)

        if not success:
            raise HTTPException(status_code=404, detail="User not in family")

        return {
            "success": True,
            "message": "Successfully left family"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leaving family: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{family_id}")
async def delete_family(
    family_id: str,
    user_id: str = Query(..., description="User ID (must be admin)")
):
    """
    Delete a family (admin only)

    **Warning:**
    - This action is permanent
    - All members will be removed
    """
    try:
        # Verify user is admin
        family = family_storage.get_family_by_id(family_id)

        if not family:
            raise HTTPException(status_code=404, detail="Family not found")

        is_admin = any(m.user_id == user_id and m.role == "admin" for m in family.members)

        if not is_admin:
            raise HTTPException(status_code=403, detail="Only admin can delete family")

        # Delete
        success = family_storage.delete_family(family_id)

        if not success:
            raise HTTPException(status_code=404, detail="Family not found")

        return {
            "success": True,
            "message": "Family deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting family: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invite-code/{invite_code}/verify")
async def verify_invite_code(invite_code: str):
    """
    Verify an invite code is valid

    **Returns:**
    - Family name and member count if valid
    - Error if invalid
    """
    try:
        family = family_storage.get_family_by_invite_code(invite_code.upper())

        if not family:
            raise HTTPException(status_code=404, detail="Invalid invite code")

        return {
            "valid": True,
            "family_name": family.name,
            "member_count": len(family.members),
            "created_at": family.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying invite code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
