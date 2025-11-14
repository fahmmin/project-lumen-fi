"""
PROJECT LUMEN - Financial Goal Models
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class GoalStatus(str, Enum):
    """Goal status enum"""
    ON_TRACK = "on_track"
    AHEAD = "ahead"
    BEHIND = "behind"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class GoalPriority(str, Enum):
    """Goal priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GoalCreate(BaseModel):
    """Goal creation model"""
    user_id: str = Field(..., description="User ID")
    name: str = Field(..., description="Goal name (e.g., 'Buy a Car')")
    target_amount: float = Field(..., gt=0, description="Target amount needed")
    target_date: date = Field(..., description="Target completion date")
    current_savings: float = Field(default=0.0, ge=0, description="Current savings toward goal")
    priority: GoalPriority = Field(default=GoalPriority.MEDIUM, description="Goal priority")


class GoalUpdate(BaseModel):
    """Goal update model"""
    name: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    target_date: Optional[date] = None
    current_savings: Optional[float] = Field(None, ge=0)
    priority: Optional[GoalPriority] = None
    status: Optional[GoalStatus] = None


class FinancialGoal(BaseModel):
    """Complete financial goal model"""
    goal_id: str
    user_id: str
    name: str
    target_amount: float
    target_date: date
    current_savings: float = 0.0
    progress_percentage: float = 0.0
    status: GoalStatus = GoalStatus.ON_TRACK
    priority: GoalPriority = GoalPriority.MEDIUM
    monthly_contribution: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
