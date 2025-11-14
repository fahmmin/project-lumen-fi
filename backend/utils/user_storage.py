"""
PROJECT LUMEN - User Storage Manager
Handles user profile, goals, and related data persistence
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from backend.models.user import UserProfile, UserProfileCreate, UserProfileUpdate
from backend.models.goal import FinancialGoal, GoalCreate, GoalUpdate
from backend.utils.logger import logger


class UserStorage:
    """Manages user data persistence"""

    def __init__(self, data_dir: str = "backend/data/user_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_user_dir(self, user_id: str) -> Path:
        """Get user's data directory"""
        user_dir = self.data_dir / user_id
        user_dir.mkdir(exist_ok=True)
        return user_dir

    def _get_profile_path(self, user_id: str) -> Path:
        """Get path to user's profile file"""
        return self._get_user_dir(user_id) / "profile.json"

    def _get_goals_path(self, user_id: str) -> Path:
        """Get path to user's goals file"""
        return self._get_user_dir(user_id) / "goals.json"

    # ==================== USER PROFILE ====================

    def create_profile(self, profile_data: UserProfileCreate) -> UserProfile:
        """
        Create a new user profile

        Args:
            profile_data: User profile creation data

        Returns:
            Created user profile

        Raises:
            FileExistsError: If profile already exists
        """
        user_id = profile_data.user_id
        profile_path = self._get_profile_path(user_id)

        if profile_path.exists():
            raise FileExistsError(f"Profile for user {user_id} already exists")

        # Create profile with defaults for optional fields
        profile_dict = profile_data.dict()
        # Provide defaults for optional fields if not provided
        if profile_dict.get('name') is None:
            # Use first 8 chars of user_id, removing 0x prefix if present
            display_id = user_id.replace('0x', '')[:8] if user_id.startswith('0x') else user_id[:8]
            profile_dict['name'] = f"User {display_id}"
        if profile_dict.get('email') is None:
            # Use a valid email format for EmailStr validation
            # Sanitize user_id for email (remove 0x, take first 8 chars, lowercase, alphanumeric only)
            email_id = user_id.replace('0x', '').lower()[:8]
            email_id = ''.join(c for c in email_id if c.isalnum())
            if not email_id:
                email_id = 'user'
            # Use a valid domain that EmailStr accepts (not .local)
            profile_dict['email'] = f"{email_id}@example.com"
        if profile_dict.get('salary_monthly') is None:
            profile_dict['salary_monthly'] = 0.0
        
        profile = UserProfile(**profile_dict)

        # Save to file
        self._save_json(profile_path, profile.dict())

        logger.info(f"Created profile for user {user_id}")
        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile

        Args:
            user_id: User ID

        Returns:
            User profile or None if not found
        """
        profile_path = self._get_profile_path(user_id)

        if not profile_path.exists():
            return None

        data = self._load_json(profile_path)
        return UserProfile(**data)

    def update_profile(self, user_id: str, update_data: UserProfileUpdate) -> UserProfile:
        """
        Update user profile

        Args:
            user_id: User ID
            update_data: Profile update data

        Returns:
            Updated profile

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        profile = self.get_profile(user_id)
        if not profile:
            raise FileNotFoundError(f"Profile for user {user_id} not found")

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)

        profile.updated_at = datetime.now()

        # Save
        self._save_json(self._get_profile_path(user_id), profile.dict())

        logger.info(f"Updated profile for user {user_id}")
        return profile

    def ensure_profile_exists(self, user_id: str) -> UserProfile:
        """
        Ensure user profile exists, create if it doesn't
        Also registers user in MongoDB if connected
        
        Args:
            user_id: User ID
            
        Returns:
            User profile (existing or newly created)
        """
        profile = self.get_profile(user_id)
        if not profile:
            logger.info(f"Auto-creating profile for user {user_id}")
            from backend.models.user import UserProfileCreate
            profile_data = UserProfileCreate(user_id=user_id)
            profile = self.create_profile(profile_data)
            
            # Register user in MongoDB (silently, don't expose to frontend)
            try:
                from backend.utils.mongo_storage import get_mongo_storage
                mongo_storage = get_mongo_storage()
                mongo_storage.register_user(user_id, user_id)
            except Exception as mongo_error:
                # Silently fail - MongoDB is optional
                logger.debug(f"MongoDB user registration failed (non-critical): {mongo_error}")
        return profile

    def delete_profile(self, user_id: str) -> Dict:
        """
        Delete user profile and all associated data

        Args:
            user_id: User ID

        Returns:
            Deletion summary
        """
        user_dir = self._get_user_dir(user_id)

        if not user_dir.exists():
            raise FileNotFoundError(f"User {user_id} not found")

        # Count data before deletion
        goals = self.list_goals(user_id)
        receipt_dir = user_dir / "receipts"
        receipt_count = len(list(receipt_dir.glob("*"))) if receipt_dir.exists() else 0

        # Delete entire user directory
        import shutil
        shutil.rmtree(user_dir)

        logger.info(f"Deleted all data for user {user_id}")

        return {
            "user_id": user_id,
            "deleted_goals": len(goals),
            "deleted_receipts": receipt_count
        }

    def list_all_users(self) -> List[UserProfile]:
        """
        List all user profiles

        Returns:
            List of all user profiles
        """
        profiles = []
        for user_dir in self.data_dir.iterdir():
            if user_dir.is_dir():
                profile = self.get_profile(user_dir.name)
                if profile:
                    profiles.append(profile)

        return profiles

    # ==================== GOALS ====================

    def create_goal(self, goal_data: GoalCreate) -> FinancialGoal:
        """
        Create a new financial goal

        Args:
            goal_data: Goal creation data

        Returns:
            Created goal
        """
        user_id = goal_data.user_id

        # Auto-create user profile if it doesn't exist
        if not self.get_profile(user_id):
            from backend.models.user import UserProfileCreate
            logger.info(f"Auto-creating profile for user {user_id}")
            profile_data = UserProfileCreate(user_id=user_id)
            self.create_profile(profile_data)

        # Generate goal ID
        import uuid
        goal_id = f"goal_{uuid.uuid4().hex[:12]}"

        try:
            # Create goal dict with all required fields
            goal_dict = goal_data.dict()
            goal_dict['goal_id'] = goal_id
            
            # Ensure target_amount is not zero to avoid division by zero
            if goal_dict.get('target_amount', 0) <= 0:
                raise ValueError("target_amount must be greater than 0")
            
            # Create goal - Pydantic will handle type conversions
            goal = FinancialGoal(**goal_dict)

            # Calculate progress (handle division by zero)
            if goal.target_amount > 0:
                goal.progress_percentage = (goal.current_savings / goal.target_amount) * 100
            else:
                goal.progress_percentage = 0.0
        except Exception as e:
            logger.error(f"Error creating FinancialGoal object: {e}", exc_info=True)
            raise ValueError(f"Invalid goal data: {str(e)}")

        # Load existing goals
        goals = self._load_goals(user_id)

        # Add new goal - use dict() with proper serialization
        try:
            goal_dict = goal.dict()
            goals.append(goal_dict)
        except Exception as e:
            logger.error(f"Error serializing goal to dict: {e}", exc_info=True)
            raise ValueError(f"Failed to serialize goal: {str(e)}")

        # Save
        try:
            self._save_json(self._get_goals_path(user_id), goals)
        except Exception as e:
            logger.error(f"Error saving goals to file: {e}", exc_info=True)
            raise ValueError(f"Failed to save goal: {str(e)}")

        logger.info(f"Created goal {goal_id} for user {user_id}")
        return goal

    def get_goal(self, goal_id: str, user_id: str) -> Optional[FinancialGoal]:
        """
        Get a specific goal

        Args:
            goal_id: Goal ID
            user_id: User ID

        Returns:
            Goal or None if not found
        """
        goals = self._load_goals(user_id)

        for goal_data in goals:
            if goal_data.get("goal_id") == goal_id:
                return FinancialGoal(**goal_data)

        return None

    def list_goals(self, user_id: str) -> List[FinancialGoal]:
        """
        List all goals for a user

        Args:
            user_id: User ID

        Returns:
            List of goals
        """
        goals_data = self._load_goals(user_id)
        return [FinancialGoal(**g) for g in goals_data]

    def update_goal(self, goal_id: str, user_id: str, update_data: GoalUpdate) -> FinancialGoal:
        """
        Update a goal

        Args:
            goal_id: Goal ID
            user_id: User ID
            update_data: Update data

        Returns:
            Updated goal

        Raises:
            FileNotFoundError: If goal not found
        """
        goals = self._load_goals(user_id)

        # Find and update goal
        goal_found = False
        updated_goal = None

        for i, goal_data in enumerate(goals):
            if goal_data.get("goal_id") == goal_id:
                goal = FinancialGoal(**goal_data)

                # Update fields
                update_dict = update_data.dict(exclude_unset=True)
                for key, value in update_dict.items():
                    setattr(goal, key, value)

                # Recalculate progress
                goal.progress_percentage = (goal.current_savings / goal.target_amount) * 100
                goal.updated_at = datetime.now()

                goals[i] = goal.dict()
                updated_goal = goal
                goal_found = True
                break

        if not goal_found:
            raise FileNotFoundError(f"Goal {goal_id} not found for user {user_id}")

        # Save
        self._save_json(self._get_goals_path(user_id), goals)

        logger.info(f"Updated goal {goal_id} for user {user_id}")
        return updated_goal

    def delete_goal(self, goal_id: str, user_id: str) -> None:
        """
        Delete a goal

        Args:
            goal_id: Goal ID
            user_id: User ID

        Raises:
            FileNotFoundError: If goal not found
        """
        goals = self._load_goals(user_id)

        # Filter out the goal
        new_goals = [g for g in goals if g.get("goal_id") != goal_id]

        if len(new_goals) == len(goals):
            raise FileNotFoundError(f"Goal {goal_id} not found for user {user_id}")

        # Save
        self._save_json(self._get_goals_path(user_id), new_goals)

        logger.info(f"Deleted goal {goal_id} for user {user_id}")

    # ==================== HELPER METHODS ====================

    def _load_goals(self, user_id: str) -> List[Dict]:
        """Load goals for a user"""
        goals_path = self._get_goals_path(user_id)

        if not goals_path.exists():
            return []

        return self._load_json(goals_path)

    def _save_json(self, path: Path, data: any) -> None:
        """Save data to JSON file"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _load_json(self, path: Path) -> any:
        """Load data from JSON file"""
        with open(path, 'r') as f:
            return json.load(f)


# Global storage instance
_user_storage = None


def get_user_storage() -> UserStorage:
    """Get global user storage instance"""
    global _user_storage
    if _user_storage is None:
        _user_storage = UserStorage()
    return _user_storage
