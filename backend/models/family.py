"""
Family and Shared Budget Models - Phase 2
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class FamilyRole(str, Enum):
    """Member roles in family"""
    ADMIN = "admin"  # Created the family, can manage members
    MEMBER = "member"  # Regular member


class FamilyMember(BaseModel):
    """Family member"""
    user_id: str
    role: FamilyRole
    joined_at: datetime = Field(default_factory=datetime.now)
    display_name: Optional[str] = None


class Family(BaseModel):
    """Family/household group for shared budgets"""
    family_id: str
    name: str
    invite_code: str  # 6-character code for joining
    created_by: str  # user_id of creator
    created_at: datetime = Field(default_factory=datetime.now)
    members: List[FamilyMember] = Field(default_factory=list)
    shared_budget: Optional[Dict[str, float]] = None  # Category -> Amount
    description: Optional[str] = None


class FamilyCreate(BaseModel):
    """Request to create a family"""
    name: str = Field(..., min_length=1, max_length=100)
    created_by: str
    description: Optional[str] = None
    shared_budget: Optional[Dict[str, float]] = None


class FamilyJoin(BaseModel):
    """Request to join a family"""
    invite_code: str = Field(..., min_length=6, max_length=6)
    user_id: str
    display_name: Optional[str] = None


class FamilyDashboard(BaseModel):
    """Aggregated family dashboard"""
    family_id: str
    family_name: str
    period: str
    member_count: int
    summary: Dict
    spending_by_member: List[Dict]
    spending_by_category: Dict[str, float]
    shared_budget_status: Optional[Dict] = None
    top_spenders: List[Dict]
    insights: List[str]


class FamilyMemberStats(BaseModel):
    """Individual member stats within family"""
    user_id: str
    display_name: str
    total_spent: float
    spending_by_category: Dict[str, float]
    percentage_of_family_spending: float
    compared_to_family_avg: Dict  # above/below average


class FamilyUpdate(BaseModel):
    """Update family settings"""
    name: Optional[str] = None
    description: Optional[str] = None
    shared_budget: Optional[Dict[str, float]] = None
