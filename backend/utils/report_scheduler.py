"""
Report Scheduler - Automated Weekly/Monthly Report Generation
Uses APScheduler to send scheduled financial reports via email
"""

from typing import Dict, List, Optional
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
import asyncio
import json
from pathlib import Path

from backend.config import settings
from backend.utils.logger import logger
from backend.utils.user_storage import get_user_storage
from backend.agents.report_generation_agent import get_report_generator
from backend.utils.comprehensive_report_generator import get_comprehensive_report_generator
from backend.utils.email_service import get_email_service
from backend.models.user import UserProfile


class ReportScheduler:
    """
    Manages scheduled report generation and email delivery
    """

    def __init__(self):
        """Initialize scheduler"""
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            timezone='UTC'
        )
        self.user_storage = get_user_storage()
        self.report_generator = get_report_generator()
        self.report_file_generator = get_comprehensive_report_generator()
        self.email_service = get_email_service()

        # Storage for user schedules
        self.schedules_file = settings.DATA_DIR / "report_schedules.json"
        self.user_schedules: Dict[str, Dict] = self._load_schedules()

        self.is_running = False

    def _load_schedules(self) -> Dict[str, Dict]:
        """Load user report schedules from file"""
        if self.schedules_file.exists():
            try:
                with open(self.schedules_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading schedules: {e}")
        return {}

    def _save_schedules(self):
        """Save user report schedules to file"""
        try:
            with open(self.schedules_file, 'w') as f:
                json.dump(self.user_schedules, f, indent=2)
            logger.info("Report schedules saved")
        except Exception as e:
            logger.error(f"Error saving schedules: {e}")

    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            if settings.SCHEDULED_REPORTS_ENABLED:
                self.scheduler.start()
                self.is_running = True
                logger.info("Report scheduler started")

                # Restore all saved schedules
                self._restore_schedules()
            else:
                logger.info("Scheduled reports disabled in configuration")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Report scheduler shut down")

    def _restore_schedules(self):
        """Restore all saved schedules"""
        for user_id, schedule_config in self.user_schedules.items():
            try:
                self._schedule_user_report(user_id, schedule_config, restore=True)
                logger.info(f"Restored schedule for user {user_id}")
            except Exception as e:
                logger.error(f"Error restoring schedule for {user_id}: {e}")

    def schedule_weekly_report(
        self,
        user_id: str,
        email: str,
        day_of_week: int = 1,  # 0=Monday, 6=Sunday
        hour: int = 8,
        minute: int = 0
    ) -> bool:
        """
        Schedule weekly report for a user

        Args:
            user_id: User ID
            email: Email address to send report to
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)

        Returns:
            bool: Success status
        """
        schedule_config = {
            "frequency": "weekly",
            "email": email,
            "day_of_week": day_of_week,
            "hour": hour,
            "minute": minute,
            "enabled": True
        }

        return self._schedule_user_report(user_id, schedule_config)

    def schedule_monthly_report(
        self,
        user_id: str,
        email: str,
        day_of_month: int = 1,
        hour: int = 8,
        minute: int = 0
    ) -> bool:
        """
        Schedule monthly report for a user

        Args:
            user_id: User ID
            email: Email address
            day_of_month: Day of month (1-28)
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)

        Returns:
            bool: Success status
        """
        schedule_config = {
            "frequency": "monthly",
            "email": email,
            "day_of_month": min(28, max(1, day_of_month)),  # Ensure 1-28
            "hour": hour,
            "minute": minute,
            "enabled": True
        }

        return self._schedule_user_report(user_id, schedule_config)

    def _schedule_user_report(
        self,
        user_id: str,
        schedule_config: Dict,
        restore: bool = False
    ) -> bool:
        """Schedule report generation for a user"""
        try:
            # Remove existing job if any
            job_id = f"report_{user_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # Create cron trigger based on frequency
            frequency = schedule_config.get("frequency", "weekly")
            hour = schedule_config.get("hour", 8)
            minute = schedule_config.get("minute", 0)

            if frequency == "weekly":
                day_of_week = schedule_config.get("day_of_week", 1)
                trigger = CronTrigger(
                    day_of_week=day_of_week,
                    hour=hour,
                    minute=minute,
                    timezone='UTC'
                )
            elif frequency == "monthly":
                day_of_month = schedule_config.get("day_of_month", 1)
                trigger = CronTrigger(
                    day=day_of_month,
                    hour=hour,
                    minute=minute,
                    timezone='UTC'
                )
            else:
                logger.error(f"Invalid frequency: {frequency}")
                return False

            # Schedule the job
            self.scheduler.add_job(
                func=self._generate_and_email_report,
                trigger=trigger,
                id=job_id,
                args=[user_id, schedule_config],
                replace_existing=True
            )

            # Save schedule
            self.user_schedules[user_id] = schedule_config
            self._save_schedules()

            if not restore:
                logger.info(f"Scheduled {frequency} report for user {user_id}")

            return True

        except Exception as e:
            logger.error(f"Error scheduling report for {user_id}: {e}")
            return False

    async def _generate_and_email_report(
        self,
        user_id: str,
        schedule_config: Dict
    ):
        """
        Generate report and email it to user
        This is the core function called by the scheduler
        """
        try:
            logger.info(f"Starting scheduled report generation for user {user_id}")

            email = schedule_config.get("email")
            if not email:
                logger.error(f"No email configured for user {user_id}")
                return

            # Get user profile for name
            try:
                profile = self.user_storage.get_profile(user_id)
                user_name = profile.full_name if profile else "Valued User"
            except:
                user_name = "Valued User"

            # Determine report type based on frequency
            frequency = schedule_config.get("frequency", "weekly")
            report_type = "monthly" if frequency == "monthly" else "weekly"

            # Step 1: Generate comprehensive report using agentic RAG
            logger.info(f"Generating {report_type} report for {user_id}")
            report_data = self.report_generator.generate_comprehensive_report(
                user_id=user_id,
                report_type=report_type,
                include_attachments=True
            )

            # Step 2: Generate HTML report file
            logger.info(f"Creating {report_type} report file")
            report_file_path = await self.report_file_generator.generate_comprehensive_report(
                report_data=report_data,
                format="html"
            )

            # Step 3: Prepare email summary data
            executive_summary = report_data.get("executive_summary", {})
            financial_overview = report_data.get("financial_overview", {})
            goal_progress = report_data.get("goal_progress", {})
            savings_opportunities = report_data.get("savings_opportunities", {})

            email_summary = {
                "period": report_data.get("report_metadata", {}).get("period", "This Period"),
                "total_spending": executive_summary.get("total_spending", 0),
                "budget_status": {
                    "total_budget": financial_overview.get("budget_status", {}).get("total_budget", 0),
                    "used": financial_overview.get("budget_status", {}).get("used", 0),
                    "remaining": financial_overview.get("budget_status", {}).get("remaining", 0)
                },
                "top_categories": financial_overview.get("top_categories", []),
                "alerts": [
                    {
                        "level": h.get("type", "info"),
                        "message": h.get("message", "")
                    }
                    for h in executive_summary.get("key_highlights", [])
                ],
                "savings_opportunities": savings_opportunities.get("opportunities", []),
                "goal_progress": goal_progress.get("goals", [])
            }

            # Step 4: Send email with report
            logger.info(f"Sending report email to {email}")
            email_sent = self.email_service.send_weekly_report_email(
                to_email=email,
                to_name=user_name,
                report_summary=email_summary,
                report_file_path=report_file_path
            )

            if email_sent:
                logger.info(f"Successfully sent {report_type} report to {email}")
            else:
                logger.error(f"Failed to send report email to {email}")

        except Exception as e:
            logger.error(f"Error in scheduled report generation for {user_id}: {e}", exc_info=True)

    def generate_report_now(
        self,
        user_id: str,
        email: str,
        report_type: str = "weekly"
    ) -> asyncio.Task:
        """
        Generate and send report immediately (on-demand)

        Args:
            user_id: User ID
            email: Email address
            report_type: "weekly", "monthly", "quarterly", or "yearly"

        Returns:
            Asyncio task
        """
        schedule_config = {
            "frequency": report_type,
            "email": email
        }

        # Create and return async task
        return asyncio.create_task(
            self._generate_and_email_report(user_id, schedule_config)
        )

    def unschedule_report(self, user_id: str) -> bool:
        """
        Unschedule report for a user

        Args:
            user_id: User ID

        Returns:
            bool: Success status
        """
        try:
            job_id = f"report_{user_id}"

            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Unscheduled report for user {user_id}")

            # Remove from saved schedules
            if user_id in self.user_schedules:
                del self.user_schedules[user_id]
                self._save_schedules()

            return True

        except Exception as e:
            logger.error(f"Error unscheduling report for {user_id}: {e}")
            return False

    def get_user_schedule(self, user_id: str) -> Optional[Dict]:
        """Get schedule configuration for a user"""
        return self.user_schedules.get(user_id)

    def list_all_schedules(self) -> Dict[str, Dict]:
        """Get all scheduled reports"""
        return self.user_schedules.copy()


# Global scheduler instance
_report_scheduler = None


def get_report_scheduler() -> ReportScheduler:
    """Get global report scheduler instance"""
    global _report_scheduler
    if _report_scheduler is None:
        _report_scheduler = ReportScheduler()
    return _report_scheduler
