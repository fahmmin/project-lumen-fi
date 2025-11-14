"""
Gamification Agent - Points, Badges, Streaks, Leaderboards
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta, date
from backend.models.achievement import (
    UserPoints, Badge, BadgeLevel, AchievementType,
    LeaderboardEntry, PointsActivity, GamificationStats
)
from backend.utils.logger import logger
import json
import os


class GamificationAgent:
    """Manages gamification: points, badges, streaks, achievements"""

    # Points awarded for activities
    POINTS_SYSTEM = {
        "upload_receipt": 10,
        "create_goal": 50,
        "complete_goal": 200,
        "update_budget": 20,
        "stay_under_budget": 100,
        "daily_login": 5,
        "weekly_streak": 50,
        "monthly_streak": 200,
        "share_with_family": 30,
        "analyze_spending": 15,
        "save_money": 25,
    }

    # Level thresholds
    LEVEL_THRESHOLDS = [0, 100, 300, 600, 1000, 1500, 2200, 3000, 4000, 5200, 6600]

    def __init__(self):
        self.data_dir = "backend/data/gamification"
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_user_file(self, user_id: str) -> str:
        """Get path to user's gamification file"""
        return os.path.join(self.data_dir, f"{user_id}_gamification.json")

    def _load_user_points(self, user_id: str) -> UserPoints:
        """Load user's gamification data"""
        file_path = self._get_user_file(user_id)

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Convert datetime strings back
                if data.get('last_activity'):
                    data['last_activity'] = datetime.fromisoformat(data['last_activity'])
                for achievement in data.get('achievements', []):
                    if achievement.get('unlocked_at'):
                        achievement['unlocked_at'] = datetime.fromisoformat(achievement['unlocked_at'])
                return UserPoints(**data)

        # Initialize new user
        return UserPoints(
            user_id=user_id,
            achievements=self._get_all_badges(unlocked=False)
        )

    def _save_user_points(self, user_points: UserPoints):
        """Save user's gamification data"""
        file_path = self._get_user_file(user_points.user_id)

        # Convert to dict and handle datetimes
        data = user_points.model_dump()
        if data.get('last_activity'):
            data['last_activity'] = data['last_activity'].isoformat()
        for achievement in data.get('achievements', []):
            if achievement.get('unlocked_at'):
                achievement['unlocked_at'] = achievement['unlocked_at'].isoformat()

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_all_badges(self, unlocked: bool = False) -> List[Badge]:
        """Get all possible badges"""
        badges = [
            # Streak badges
            Badge(
                badge_id="streak_week",
                name="Week Warrior",
                description="Log in for 7 days in a row",
                type=AchievementType.STREAK,
                level=BadgeLevel.BRONZE,
                icon="🔥",
                points=50,
                requirement="7_day_streak",
                unlocked=unlocked
            ),
            Badge(
                badge_id="streak_month",
                name="Monthly Master",
                description="Log in for 30 days in a row",
                type=AchievementType.STREAK,
                level=BadgeLevel.GOLD,
                icon="⚡",
                points=200,
                requirement="30_day_streak",
                unlocked=unlocked
            ),

            # Savings badges
            Badge(
                badge_id="saver_bronze",
                name="Penny Pincher",
                description="Save $500",
                type=AchievementType.SAVINGS,
                level=BadgeLevel.BRONZE,
                icon="💰",
                points=50,
                requirement="save_500",
                unlocked=unlocked
            ),
            Badge(
                badge_id="saver_silver",
                name="Smart Saver",
                description="Save $2,000",
                type=AchievementType.SAVINGS,
                level=BadgeLevel.SILVER,
                icon="💎",
                points=100,
                requirement="save_2000",
                unlocked=unlocked
            ),
            Badge(
                badge_id="saver_gold",
                name="Wealth Builder",
                description="Save $10,000",
                type=AchievementType.SAVINGS,
                level=BadgeLevel.GOLD,
                icon="🏆",
                points=300,
                requirement="save_10000",
                unlocked=unlocked
            ),

            # Budget badges
            Badge(
                badge_id="budget_master",
                name="Budget Master",
                description="Stay under budget for 3 months",
                type=AchievementType.BUDGET,
                level=BadgeLevel.SILVER,
                icon="📊",
                points=150,
                requirement="under_budget_3_months",
                unlocked=unlocked
            ),

            # Goal badges
            Badge(
                badge_id="goal_creator",
                name="Goal Setter",
                description="Create your first financial goal",
                type=AchievementType.GOAL,
                level=BadgeLevel.BRONZE,
                icon="🎯",
                points=50,
                requirement="create_1_goal",
                unlocked=unlocked
            ),
            Badge(
                badge_id="goal_achiever",
                name="Goal Crusher",
                description="Complete a financial goal",
                type=AchievementType.GOAL,
                level=BadgeLevel.GOLD,
                icon="✨",
                points=250,
                requirement="complete_1_goal",
                unlocked=unlocked
            ),

            # Milestone badges
            Badge(
                badge_id="receipt_100",
                name="Receipt Collector",
                description="Upload 100 receipts",
                type=AchievementType.MILESTONE,
                level=BadgeLevel.SILVER,
                icon="🧾",
                points=100,
                requirement="upload_100_receipts",
                unlocked=unlocked
            ),
            Badge(
                badge_id="analyzer",
                name="Data Analyst",
                description="Check your dashboard 50 times",
                type=AchievementType.MILESTONE,
                level=BadgeLevel.BRONZE,
                icon="📈",
                points=75,
                requirement="check_dashboard_50",
                unlocked=unlocked
            ),
        ]

        return badges

    def award_points(self, user_id: str, activity: str, metadata: Optional[Dict] = None) -> Dict:
        """Award points for an activity"""
        user_points = self._load_user_points(user_id)

        points = self.POINTS_SYSTEM.get(activity, 0)
        if points == 0:
            return {"success": False, "message": "Unknown activity"}

        # Award points
        old_level = user_points.level
        user_points.total_points += points
        user_points.last_activity = datetime.now()

        # Update streak for daily login
        if activity == "daily_login":
            self._update_streak(user_points)

        # Calculate new level
        new_level = self._calculate_level(user_points.total_points)
        user_points.level = new_level

        # Check for newly unlocked badges
        newly_unlocked = self._check_achievements(user_points, activity, metadata)

        # Save
        self._save_user_points(user_points)

        return {
            "success": True,
            "points_earned": points,
            "total_points": user_points.total_points,
            "level": new_level,
            "level_up": new_level > old_level,
            "badges_unlocked": newly_unlocked,
            "current_streak": user_points.current_streak
        }

    def _update_streak(self, user_points: UserPoints):
        """Update login streak"""
        now = datetime.now()

        if user_points.last_activity is None:
            # First login
            user_points.current_streak = 1
        else:
            last_date = user_points.last_activity.date()
            today = now.date()
            days_diff = (today - last_date).days

            if days_diff == 1:
                # Consecutive day
                user_points.current_streak += 1
            elif days_diff > 1:
                # Streak broken
                user_points.current_streak = 1
            # Same day login doesn't affect streak

        # Update longest streak
        if user_points.current_streak > user_points.longest_streak:
            user_points.longest_streak = user_points.current_streak

    def _calculate_level(self, total_points: int) -> int:
        """Calculate user level based on points"""
        level = 1
        for threshold in self.LEVEL_THRESHOLDS:
            if total_points >= threshold:
                level += 1
            else:
                break
        return level - 1

    def _check_achievements(self, user_points: UserPoints, activity: str, metadata: Optional[Dict]) -> List[str]:
        """Check and unlock achievements"""
        newly_unlocked = []

        for achievement in user_points.achievements:
            if achievement.unlocked:
                continue

            unlocked = False

            # Check streak achievements
            if achievement.requirement == "7_day_streak" and user_points.current_streak >= 7:
                unlocked = True
            elif achievement.requirement == "30_day_streak" and user_points.current_streak >= 30:
                unlocked = True

            # Check savings achievements (would need savings data)
            elif achievement.requirement == "save_500" and metadata and metadata.get("total_savings", 0) >= 500:
                unlocked = True
            elif achievement.requirement == "save_2000" and metadata and metadata.get("total_savings", 0) >= 2000:
                unlocked = True
            elif achievement.requirement == "save_10000" and metadata and metadata.get("total_savings", 0) >= 10000:
                unlocked = True

            # Check goal achievements
            elif achievement.requirement == "create_1_goal" and activity == "create_goal":
                unlocked = True
            elif achievement.requirement == "complete_1_goal" and activity == "complete_goal":
                unlocked = True

            # Check milestone achievements
            elif achievement.requirement == "upload_100_receipts" and metadata and metadata.get("receipt_count", 0) >= 100:
                unlocked = True
            elif achievement.requirement == "check_dashboard_50" and metadata and metadata.get("dashboard_views", 0) >= 50:
                unlocked = True

            if unlocked:
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now()
                user_points.badges_earned.append(achievement.badge_id)
                user_points.total_points += achievement.points
                newly_unlocked.append(achievement.name)

        return newly_unlocked

    def get_user_stats(self, user_id: str) -> GamificationStats:
        """Get complete gamification stats for user"""
        user_points = self._load_user_points(user_id)

        # Calculate progress to next level
        current_level = user_points.level
        current_threshold = self.LEVEL_THRESHOLDS[current_level] if current_level < len(self.LEVEL_THRESHOLDS) else self.LEVEL_THRESHOLDS[-1]
        next_threshold = self.LEVEL_THRESHOLDS[current_level + 1] if current_level + 1 < len(self.LEVEL_THRESHOLDS) else current_threshold + 1000

        points_in_level = user_points.total_points - current_threshold
        points_needed = next_threshold - current_threshold
        progress = points_in_level / points_needed if points_needed > 0 else 1.0

        # Count badges
        badges_earned = sum(1 for b in user_points.achievements if b.unlocked)
        badges_total = len(user_points.achievements)

        # Find next achievable badges
        next_badges = [b for b in user_points.achievements if not b.unlocked][:3]

        # Get leaderboard position
        rank, percentile = self._get_user_rank(user_id)

        return GamificationStats(
            user_id=user_id,
            total_points=user_points.total_points,
            level=user_points.level,
            progress_to_next_level=progress,
            badges_earned=badges_earned,
            badges_total=badges_total,
            current_streak=user_points.current_streak,
            longest_streak=user_points.longest_streak,
            leaderboard_rank=rank,
            percentile=percentile,
            next_badges=next_badges
        )

    def get_leaderboard(self, limit: int = 10, current_user_id: Optional[str] = None) -> List[LeaderboardEntry]:
        """Get top users leaderboard"""
        all_users = []

        # Load all user gamification files
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith("_gamification.json"):
                    user_id = filename.replace("_gamification.json", "")
                    user_points = self._load_user_points(user_id)

                    badges_count = sum(1 for b in user_points.achievements if b.unlocked)

                    all_users.append({
                        "user_id": user_id,
                        "total_points": user_points.total_points,
                        "level": user_points.level,
                        "badge_count": badges_count
                    })

        # Sort by points
        all_users.sort(key=lambda x: x["total_points"], reverse=True)

        # Create leaderboard entries
        leaderboard = []
        for rank, user_data in enumerate(all_users[:limit], start=1):
            # Anonymize names (except current user)
            is_current = user_data["user_id"] == current_user_id
            display_name = "You" if is_current else f"User_{user_data['user_id'][:4]}"

            leaderboard.append(LeaderboardEntry(
                rank=rank,
                user_id=user_data["user_id"],
                display_name=display_name,
                total_points=user_data["total_points"],
                level=user_data["level"],
                badge_count=user_data["badge_count"],
                is_current_user=is_current
            ))

        return leaderboard

    def _get_user_rank(self, user_id: str) -> tuple[Optional[int], Optional[float]]:
        """Get user's rank and percentile"""
        all_points = []
        user_points_val = 0

        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith("_gamification.json"):
                    uid = filename.replace("_gamification.json", "")
                    up = self._load_user_points(uid)
                    all_points.append(up.total_points)
                    if uid == user_id:
                        user_points_val = up.total_points

        if not all_points:
            return None, None

        all_points.sort(reverse=True)
        rank = all_points.index(user_points_val) + 1 if user_points_val in all_points else None

        # Calculate percentile
        if rank:
            percentile = (1 - (rank / len(all_points))) * 100
        else:
            percentile = None

        return rank, percentile

    def get_user_badges(self, user_id: str) -> Dict:
        """Get all badges for user (earned and unearned)"""
        user_points = self._load_user_points(user_id)

        earned = [b for b in user_points.achievements if b.unlocked]
        unearned = [b for b in user_points.achievements if not b.unlocked]

        return {
            "earned_badges": earned,
            "unearned_badges": unearned,
            "total_earned": len(earned),
            "total_available": len(user_points.achievements)
        }
