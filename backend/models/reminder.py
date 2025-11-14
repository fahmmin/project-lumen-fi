"""
PROJECT LUMEN - Reminder and Pattern Models
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum
from typing import Optional


class ReminderType(str, Enum):
    """Reminder type"""
    RECURRING_EXPENSE = "recurring_expense"
    BILL_DUE = "bill_due"
    GOAL_MILESTONE = "goal_milestone"
    BUDGET_ALERT = "budget_alert"


class ReminderStatus(str, Enum):
    """Reminder status"""
    ACTIVE = "active"
    SNOOZED = "snoozed"
    DISMISSED = "dismissed"


class PatternFrequency(str, Enum):
    """Pattern frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class RecurringPattern(BaseModel):
    """Recurring spending pattern"""
    pattern_id: str
    user_id: str
    pattern_type: str = Field(..., description="Type of pattern (e.g., 'monthly_grocery')")
    vendor: str = Field(..., description="Vendor name")
    category: str = Field(..., description="Spending category")
    frequency: PatternFrequency = Field(..., description="How often it occurs")
    typical_day: Optional[int] = Field(None, ge=1, le=31, description="Typical day of month (for monthly)")
    typical_day_of_week: Optional[str] = Field(None, description="Typical day of week (for weekly)")
    typical_amount: float = Field(..., gt=0, description="Typical amount spent")
    last_purchase: date = Field(..., description="Last purchase date")
    next_expected: date = Field(..., description="Next expected purchase date")
    occurrences: int = Field(..., ge=1, description="Number of times observed")
    confidence: float = Field(..., ge=0, le=1, description="Pattern confidence (0-1)")

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class Reminder(BaseModel):
    """Reminder model"""
    reminder_id: str
    user_id: str
    reminder_type: ReminderType
    message: str = Field(..., description="Reminder message")
    category: Optional[str] = None
    typical_amount: Optional[float] = None
    typical_vendor: Optional[str] = None
    next_expected_date: Optional[date] = None
    due_date: Optional[date] = None
    confidence: float = Field(..., ge=0, le=1, description="Confidence (0-1)")
    status: ReminderStatus = Field(default=ReminderStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.now)
    snoozed_until: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
