"""
PROJECT LUMEN - User Management API Router
Handles user profile creation, updates, and management
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.models.user import (
    UserProfile,
    UserProfileCreate,
    UserProfileUpdate,
    SalaryUpdate
)
from backend.utils.user_storage import get_user_storage
from backend.utils.logger import logger

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/profile", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user_profile(profile_data: UserProfileCreate):
    """
    Create a new user profile

    Args:
        profile_data: User profile creation data

    Returns:
        Success message with user_id

    Raises:
        409: Profile already exists
        500: Internal error
    """
    try:
        storage = get_user_storage()
        profile = storage.create_profile(profile_data)

        return {
            "status": "success",
            "message": "Profile created successfully",
            "user_id": profile.user_id,
            "created_at": profile.created_at.isoformat()
        }

    except FileExistsError as e:
        logger.warning(f"Profile creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Profile for user {profile_data.user_id} already exists"
        )
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create profile"
        )


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """
    Get user profile (auto-creates if doesn't exist)

    Args:
        user_id: User ID

    Returns:
        User profile
    """
    storage = get_user_storage()
    # Auto-create profile if it doesn't exist
    profile = storage.ensure_profile_exists(user_id)
    return profile


@router.put("/profile/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, update_data: UserProfileUpdate):
    """
    Update user profile

    Args:
        user_id: User ID
        update_data: Profile update data

    Returns:
        Updated profile

    Raises:
        404: Profile not found
        500: Internal error
    """
    try:
        storage = get_user_storage()
        # Ensure profile exists first
        storage.ensure_profile_exists(user_id)
        profile = storage.update_profile(user_id, update_data)
        return profile

    except FileNotFoundError:
        # Should not happen after ensure_profile_exists, but handle just in case
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user {user_id} not found"
        )
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/{user_id}/salary", response_model=dict)
async def update_salary(user_id: str, salary_data: SalaryUpdate):
    """
    Update user's monthly salary (auto-creates profile if doesn't exist)

    Args:
        user_id: User ID
        salary_data: Salary update data

    Returns:
        Success message
    """
    try:
        storage = get_user_storage()
        # Ensure profile exists first
        storage.ensure_profile_exists(user_id)
        update_data = UserProfileUpdate(
            salary_monthly=salary_data.salary_monthly,
            currency=salary_data.currency
        )
        profile = storage.update_profile(user_id, update_data)

        return {
            "status": "success",
            "user_id": user_id,
            "salary_monthly": profile.salary_monthly,
            "currency": profile.currency,
            "updated_at": profile.updated_at.isoformat()
        }

    except FileNotFoundError:
        # Should not happen after ensure_profile_exists, but handle just in case
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user {user_id} not found"
        )


@router.delete("/profile/{user_id}", response_model=dict)
async def delete_user_profile(user_id: str):
    """
    Delete user profile and all associated data

    Args:
        user_id: User ID

    Returns:
        Deletion summary

    Raises:
        404: Profile not found
    """
    try:
        storage = get_user_storage()
        summary = storage.delete_profile(user_id)

        return {
            "status": "success",
            "message": "User data deleted successfully",
            **summary
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )


@router.get("/", response_model=List[UserProfile])
async def list_all_users():
    """
    List all user profiles

    Returns:
        List of all users
    """
    storage = get_user_storage()
    return storage.list_all_users()
