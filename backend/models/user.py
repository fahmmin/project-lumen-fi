"""
PROJECT LUMEN - User Profile Models
"""

from typing import Dict, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserProfileCreate(BaseModel):
    """User profile creation model"""
    user_id: str = Field(..., description="Unique user identifier")
    name: Optional[str] = Field(default=None, description="User's full name")
    email: Optional[EmailStr] = Field(default=None, description="User's email address")
    salary_monthly: Optional[float] = Field(default=0.0, ge=0, description="Monthly salary/income")
    currency: str = Field(default="USD", description="Currency code")
    budget_categories: Dict[str, float] = Field(
        default_factory=dict,
        description="Budget limits per category"
    )


class UserProfileUpdate(BaseModel):
    """User profile update model"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    salary_monthly: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    budget_categories: Optional[Dict[str, float]] = None


class UserProfile(BaseModel):
    """Complete user profile model"""
    user_id: str
    name: str
    email: EmailStr
    salary_monthly: float
    currency: str = "USD"
    budget_categories: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SalaryUpdate(BaseModel):
    """Salary update model"""
    salary_monthly: float = Field(..., ge=0, description="Monthly salary/income")
    currency: str = Field(default="USD", description="Currency code")
