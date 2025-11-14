"""
PROJECT LUMEN - Subscription Models
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    UNUSED = "unused"
    CANCELLED = "cancelled"


class UsageEstimate(str, Enum):
    """Usage estimate"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Subscription(BaseModel):
    """Subscription model"""
    subscription_id: str
    user_id: str
    name: str = Field(..., description="Subscription name (e.g., 'Netflix')")
    category: str = Field(default="entertainment", description="Category")
    amount: float = Field(..., gt=0, description="Subscription cost")
    frequency: str = Field(default="monthly", description="Billing frequency")
    billing_day: int = Field(..., ge=1, le=31, description="Day of month charged")
    first_detected: date = Field(..., description="First time detected")
    last_charge: date = Field(..., description="Last charge date")
    total_charges: int = Field(default=1, ge=1, description="Total number of charges")
    total_spent: float = Field(default=0.0, ge=0, description="Total amount spent")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    usage_estimate: UsageEstimate = Field(default=UsageEstimate.MEDIUM)

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }
