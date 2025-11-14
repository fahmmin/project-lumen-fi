"""
Report Models - PDF Financial Reports
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """Types of reports"""
    MONTHLY_SUMMARY = "monthly_summary"
    SPENDING_ANALYSIS = "spending_analysis"
    GOAL_PROGRESS = "goal_progress"
    TAX_SUMMARY = "tax_summary"
    CUSTOM = "custom"


class ReportRequest(BaseModel):
    """Request to generate a report"""
    user_id: str
    report_type: ReportType
    period: str = "month"  # month, quarter, year
    include_charts: bool = True
    include_insights: bool = True


class ReportMetadata(BaseModel):
    """Metadata about a generated report"""
    report_id: str
    user_id: str
    report_type: ReportType
    period: str
    generated_at: datetime = Field(default_factory=datetime.now)
    file_size: int  # bytes
    page_count: int
