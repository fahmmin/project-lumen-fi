"""
Scheduled Reports API Router
Endpoints for managing automated report generation and email delivery
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List
from datetime import datetime

from backend.utils.report_scheduler import get_report_scheduler
from backend.utils.logger import logger

router = APIRouter(prefix="/scheduled-reports", tags=["Scheduled Reports"])


# ==================== REQUEST MODELS ====================

class ScheduleWeeklyReportRequest(BaseModel):
    """Request to schedule weekly report"""
    user_id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email address to send reports to")
    day_of_week: int = Field(1, ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    hour: int = Field(8, ge=0, le=23, description="Hour of day (24-hour format)")
    minute: int = Field(0, ge=0, le=59, description="Minute of hour")


class ScheduleMonthlyReportRequest(BaseModel):
    """Request to schedule monthly report"""
    user_id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email address to send reports to")
    day_of_month: int = Field(1, ge=1, le=28, description="Day of month (1-28)")
    hour: int = Field(8, ge=0, le=23, description="Hour of day (24-hour format)")
    minute: int = Field(0, ge=0, le=59, description="Minute of hour")


class GenerateReportNowRequest(BaseModel):
    """Request to generate and email report immediately"""
    user_id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email address to send report to")
    report_type: str = Field("weekly", description="Report type: weekly, monthly, quarterly, yearly")


# ==================== API ENDPOINTS ====================

@router.post("/schedule/weekly")
async def schedule_weekly_report(request: ScheduleWeeklyReportRequest):
    """
    Schedule weekly automated reports for a user

    The report will be generated and emailed automatically every week
    using agentic RAG to analyze all financial data.
    """
    try:
        scheduler = get_report_scheduler()

        # Schedule the report
        success = scheduler.schedule_weekly_report(
            user_id=request.user_id,
            email=request.email,
            day_of_week=request.day_of_week,
            hour=request.hour,
            minute=request.minute
        )

        if success:
            # Map day_of_week to name
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_name = days[request.day_of_week]

            return {
                "success": True,
                "message": f"Weekly report scheduled for {day_name} at {request.hour:02d}:{request.minute:02d} UTC",
                "schedule": {
                    "user_id": request.user_id,
                    "email": request.email,
                    "frequency": "weekly",
                    "day_of_week": request.day_of_week,
                    "day_name": day_name,
                    "time": f"{request.hour:02d}:{request.minute:02d} UTC"
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to schedule report")

    except Exception as e:
        logger.error(f"Error scheduling weekly report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/monthly")
async def schedule_monthly_report(request: ScheduleMonthlyReportRequest):
    """
    Schedule monthly automated reports for a user

    The report will be generated and emailed automatically every month
    using agentic RAG to analyze all financial data.
    """
    try:
        scheduler = get_report_scheduler()

        # Schedule the report
        success = scheduler.schedule_monthly_report(
            user_id=request.user_id,
            email=request.email,
            day_of_month=request.day_of_month,
            hour=request.hour,
            minute=request.minute
        )

        if success:
            return {
                "success": True,
                "message": f"Monthly report scheduled for day {request.day_of_month} at {request.hour:02d}:{request.minute:02d} UTC",
                "schedule": {
                    "user_id": request.user_id,
                    "email": request.email,
                    "frequency": "monthly",
                    "day_of_month": request.day_of_month,
                    "time": f"{request.hour:02d}:{request.minute:02d} UTC"
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to schedule report")

    except Exception as e:
        logger.error(f"Error scheduling monthly report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-now")
async def generate_report_now(request: GenerateReportNowRequest, background_tasks: BackgroundTasks):
    """
    Generate and email a comprehensive financial report immediately

    This endpoint triggers on-demand report generation using agentic RAG:
    - Retrieves all relevant data using hybrid RAG (dense + sparse + reranking)
    - Coordinates multiple AI agents:
      * Personal Finance Agent - spending analysis & forecasting
      * Goal Planner Agent - goal progress tracking
      * Savings Opportunity Agent - cost reduction recommendations
      * Fraud Agent - anomaly detection
      * Pattern Agent - spending pattern analysis
      * Behavioral Agent - spending behavior insights
      * Compliance Agent - policy compliance checks
      * Audit Agent - data quality validation
    - Generates comprehensive insights and recommendations
    - Creates beautifully formatted HTML report
    - Emails report to specified address

    Perfect for when someone requests: "Generate report"
    """
    try:
        scheduler = get_report_scheduler()

        # Validate report type
        valid_types = ["weekly", "monthly", "quarterly", "yearly"]
        if request.report_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid report type. Must be one of: {', '.join(valid_types)}"
            )

        # Generate and email report in background
        task = scheduler.generate_report_now(
            user_id=request.user_id,
            email=request.email,
            report_type=request.report_type
        )

        # Add to background tasks
        background_tasks.add_task(lambda: task)

        logger.info(f"Initiated on-demand {request.report_type} report generation for {request.user_id}")

        return {
            "success": True,
            "message": f"Report generation initiated. {request.report_type.title()} report will be emailed to {request.email} shortly.",
            "details": {
                "user_id": request.user_id,
                "report_type": request.report_type,
                "email": request.email,
                "initiated_at": datetime.now().isoformat(),
                "status": "processing",
                "agents_used": [
                    "Personal Finance Agent",
                    "Goal Planner Agent",
                    "Savings Opportunity Agent",
                    "Fraud Detection Agent",
                    "Pattern Detection Agent",
                    "Behavioral Analysis Agent",
                    "Compliance Agent",
                    "Audit Agent"
                ]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report now: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedule/{user_id}")
async def unschedule_report(user_id: str):
    """
    Cancel scheduled reports for a user
    """
    try:
        scheduler = get_report_scheduler()

        success = scheduler.unschedule_report(user_id)

        if success:
            return {
                "success": True,
                "message": f"Scheduled reports cancelled for user {user_id}",
                "user_id": user_id
            }
        else:
            raise HTTPException(status_code=404, detail="No scheduled report found for this user")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unscheduling report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule/{user_id}")
async def get_user_schedule(user_id: str):
    """
    Get scheduled report configuration for a user
    """
    try:
        scheduler = get_report_scheduler()

        schedule = scheduler.get_user_schedule(user_id)

        if schedule:
            return {
                "success": True,
                "user_id": user_id,
                "schedule": schedule
            }
        else:
            return {
                "success": True,
                "user_id": user_id,
                "schedule": None,
                "message": "No scheduled report configured for this user"
            }

    except Exception as e:
        logger.error(f"Error getting user schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules")
async def list_all_schedules():
    """
    List all scheduled reports (admin endpoint)
    """
    try:
        scheduler = get_report_scheduler()

        schedules = scheduler.list_all_schedules()

        return {
            "success": True,
            "total_scheduled_reports": len(schedules),
            "schedules": schedules
        }

    except Exception as e:
        logger.error(f"Error listing schedules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def scheduler_status():
    """
    Get scheduler status and configuration
    """
    try:
        scheduler = get_report_scheduler()

        from backend.config import settings

        return {
            "success": True,
            "scheduler": {
                "enabled": settings.SCHEDULED_REPORTS_ENABLED,
                "running": scheduler.is_running,
                "default_schedule": settings.DEFAULT_REPORT_SCHEDULE,
                "default_day": settings.REPORT_GENERATION_DAY,
                "default_hour": settings.REPORT_GENERATION_HOUR
            },
            "email": {
                "configured": settings.SENDGRID_API_KEY is not None,
                "from_email": settings.SENDGRID_FROM_EMAIL,
                "from_name": settings.SENDGRID_FROM_NAME
            }
        }

    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
