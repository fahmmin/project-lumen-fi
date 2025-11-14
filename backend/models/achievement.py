"""
Achievement and Gamification Models - Phase 2
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class AchievementType(str, Enum):
    """Types of achievements"""
    STREAK = "streak"
    SAVINGS = "savings"
    BUDGET = "budget"
    GOAL = "goal"
    MILESTONE = "milestone"


class BadgeLevel(str, Enum):
    """Badge difficulty levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class Badge(BaseModel):
    """Individual badge model"""
    badge_id: str
    name: str
    description: str
    type: AchievementType
    level: BadgeLevel
    icon: str  # emoji or icon name
    points: int
    requirement: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None


class UserPoints(BaseModel):
    """User gamification points"""
    user_id: str
    total_points: int = 0
    level: int = 1
    badges_earned: List[str] = Field(default_factory=list)
    current_streak: int = 0
    longest_streak: int = 0
    last_activity: Optional[datetime] = None
    achievements: List[Badge] = Field(default_factory=list)


class LeaderboardEntry(BaseModel):
    """Leaderboard entry (anonymized)"""
    rank: int
    user_id: str  # Can be anonymized as "User_XXX"
    display_name: str
    total_points: int
    level: int
    badge_count: int
    is_current_user: bool = False


class PointsActivity(BaseModel):
    """Point-earning activity"""
    activity_type: str
    description: str
    points_earned: int
    timestamp: datetime
    badge_unlocked: Optional[str] = None


class GamificationStats(BaseModel):
    """Complete gamification statistics"""
    user_id: str
    total_points: int
    level: int
    progress_to_next_level: float  # 0.0 to 1.0
    badges_earned: int
    badges_total: int
    current_streak: int
    longest_streak: int
    leaderboard_rank: Optional[int] = None
    percentile: Optional[float] = None  # Top X%
    recent_activities: List[PointsActivity] = Field(default_factory=list)
    next_badges: List[Badge] = Field(default_factory=list)  # Close to unlocking
