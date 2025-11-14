"""
Alert Models - Real-time Fraud and Smart Alerts
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    """Types of alerts"""
    FRAUD = "fraud"
    UNUSUAL_SPENDING = "unusual_spending"
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXCEEDED = "budget_exceeded"
    GOAL_MILESTONE = "goal_milestone"
    SUBSCRIPTION_REMINDER = "subscription_reminder"
    SAVINGS_OPPORTUNITY = "savings_opportunity"
    ACHIEVEMENT = "achievement"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(BaseModel):
    """Alert model for real-time notifications"""
    alert_id: str
    user_id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    read: bool = False


class FraudAlert(Alert):
    """Specific fraud alert"""
    type: AlertType = AlertType.FRAUD
    severity: AlertSeverity = AlertSeverity.CRITICAL
    fraud_score: float  # 0.0 to 1.0
    fraud_indicators: list[str]
    transaction_id: str
    amount: float
    vendor: str


class BudgetAlert(Alert):
    """Budget warning/exceeded alert"""
    type: AlertType = AlertType.BUDGET_WARNING
    category: str
    spent: float
    budget_limit: float
    percentage_used: float


class AchievementAlert(Alert):
    """Achievement unlocked alert"""
    type: AlertType = AlertType.ACHIEVEMENT
    severity: AlertSeverity = AlertSeverity.INFO
    badge_name: str
    badge_icon: str
    points_earned: int
