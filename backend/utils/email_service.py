"""
SendGrid Email Service for Project Lumen
Handles sending financial reports and notifications via email
"""

import base64
from typing import Optional, List
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Email,
    To,
    Content,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
)
from backend.config import settings
from backend.utils.logger import logger


class EmailService:
    """SendGrid email service for sending reports"""

    def __init__(self):
        """Initialize SendGrid client"""
        self.api_key = settings.SENDGRID_API_KEY
        if not self.api_key:
            logger.warning("SendGrid API key not configured. Email sending will fail.")
            self.client = None
        else:
            self.client = SendGridAPIClient(self.api_key)

        self.from_email = Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME)

    def send_report_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        report_file_path: Optional[Path] = None,
        report_type: str = "financial_report"
    ) -> bool:
        """
        Send a financial report email with optional attachment

        Args:
            to_email: Recipient email address
            to_name: Recipient name
            subject: Email subject
            html_content: HTML email body
            report_file_path: Optional path to PDF/HTML report file to attach
            report_type: Type of report (for attachment naming)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.client:
            logger.error("SendGrid client not initialized. Cannot send email.")
            return False

        try:
            # Create email
            to_email_obj = To(to_email, to_name)
            mail = Mail(
                from_email=self.from_email,
                to_emails=to_email_obj,
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            # Add attachment if provided
            if report_file_path and report_file_path.exists():
                with open(report_file_path, 'rb') as f:
                    file_data = f.read()

                encoded_file = base64.b64encode(file_data).decode()

                # Determine file type
                file_extension = report_file_path.suffix.lower()
                if file_extension == '.pdf':
                    file_type = 'application/pdf'
                elif file_extension in ['.html', '.htm']:
                    file_type = 'text/html'
                else:
                    file_type = 'application/octet-stream'

                attachment = Attachment(
                    FileContent(encoded_file),
                    FileName(report_file_path.name),
                    FileType(file_type),
                    Disposition('attachment')
                )
                mail.attachment = attachment

            # Send email
            response = self.client.send(mail)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Report email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending report email: {e}")
            return False

    def send_weekly_report_email(
        self,
        to_email: str,
        to_name: str,
        report_summary: dict,
        report_file_path: Optional[Path] = None
    ) -> bool:
        """
        Send weekly financial report email

        Args:
            to_email: Recipient email
            to_name: Recipient name
            report_summary: Dictionary with report data
            report_file_path: Path to PDF report file

        Returns:
            bool: Success status
        """
        # Create HTML email content
        html_content = self._create_weekly_report_html(to_name, report_summary)

        subject = f"Your Weekly Financial Report - {report_summary.get('period', 'Week')}"

        return self.send_report_email(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            html_content=html_content,
            report_file_path=report_file_path,
            report_type="weekly_report"
        )

    def _create_weekly_report_html(self, to_name: str, report_summary: dict) -> str:
        """Create HTML email content for weekly report"""

        # Extract data from report summary
        period = report_summary.get('period', 'This Week')
        total_spending = report_summary.get('total_spending', 0)
        budget_status = report_summary.get('budget_status', {})
        top_categories = report_summary.get('top_categories', [])
        alerts = report_summary.get('alerts', [])
        savings_opportunities = report_summary.get('savings_opportunities', [])
        goal_progress = report_summary.get('goal_progress', [])

        # Build HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            margin: -30px -30px 30px -30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section h2 {{
            color: #667eea;
            font-size: 18px;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }}
        .stat-box {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        .stat-box .label {{
            font-size: 14px;
            color: #666;
        }}
        .stat-box .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .alert {{
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        .alert.warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        .alert.critical {{
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
        }}
        .alert.info {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
        }}
        .category-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .savings-item {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 5px;
        }}
        .goal-item {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .progress-bar {{
            background-color: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin-top: 5px;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.3s ease;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Your Weekly Financial Report</h1>
            <p style="margin: 5px 0 0 0;">Hi {to_name}, here's your financial summary for {period}</p>
        </div>

        <!-- Spending Summary -->
        <div class="section">
            <h2>📊 Spending Summary</h2>
            <div class="stat-box">
                <div class="label">Total Spending</div>
                <div class="value">${total_spending:,.2f}</div>
            </div>
"""

        # Budget status
        if budget_status:
            budget_total = budget_status.get('total_budget', 0)
            budget_used = budget_status.get('used', 0)
            budget_remaining = budget_status.get('remaining', 0)
            budget_percentage = (budget_used / budget_total * 100) if budget_total > 0 else 0

            html += f"""
            <div class="stat-box">
                <div class="label">Budget Status</div>
                <div style="margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; font-size: 14px;">
                        <span>${budget_used:,.2f} used</span>
                        <span>${budget_remaining:,.2f} remaining</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {budget_percentage:.1f}%;"></div>
                    </div>
                </div>
            </div>
"""

        # Top categories
        if top_categories:
            html += """
            <div style="margin-top: 15px;">
                <strong>Top Spending Categories:</strong>
"""
            for cat in top_categories[:5]:
                category_name = cat.get('category', 'Unknown')
                category_amount = cat.get('amount', 0)
                html += f"""
                <div class="category-item">
                    <span>{category_name}</span>
                    <span><strong>${category_amount:,.2f}</strong></span>
                </div>
"""
            html += """
            </div>
"""

        html += """
        </div>
"""

        # Alerts
        if alerts:
            html += """
        <div class="section">
            <h2>⚠️ Alerts & Warnings</h2>
"""
            for alert in alerts:
                alert_level = alert.get('level', 'info')
                alert_message = alert.get('message', '')
                html += f"""
            <div class="alert {alert_level}">
                {alert_message}
            </div>
"""
            html += """
        </div>
"""

        # Savings opportunities
        if savings_opportunities:
            html += """
        <div class="section">
            <h2>💡 Savings Opportunities</h2>
"""
            for opportunity in savings_opportunities[:3]:
                title = opportunity.get('title', '')
                description = opportunity.get('description', '')
                potential_savings = opportunity.get('potential_savings', 0)
                html += f"""
            <div class="savings-item">
                <strong>{title}</strong>
                <p style="margin: 5px 0;">{description}</p>
                <p style="margin: 5px 0; color: #28a745;">
                    <strong>Potential Savings: ${potential_savings:,.2f}</strong>
                </p>
            </div>
"""
            html += """
        </div>
"""

        # Goal progress
        if goal_progress:
            html += """
        <div class="section">
            <h2>🎯 Goal Progress</h2>
"""
            for goal in goal_progress[:3]:
                goal_name = goal.get('name', '')
                goal_current = goal.get('current', 0)
                goal_target = goal.get('target', 0)
                goal_percentage = (goal_current / goal_target * 100) if goal_target > 0 else 0
                html += f"""
            <div class="goal-item">
                <strong>{goal_name}</strong>
                <div style="display: flex; justify-content: space-between; font-size: 14px; margin-top: 5px;">
                    <span>${goal_current:,.2f} / ${goal_target:,.2f}</span>
                    <span>{goal_percentage:.1f}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {goal_percentage:.1f}%;"></div>
                </div>
            </div>
"""
            html += """
        </div>
"""

        html += """
        <div class="footer">
            <p>This report was automatically generated by Project Lumen</p>
            <p>Your AI-powered financial intelligence platform</p>
        </div>
    </div>
</body>
</html>
"""

        return html


# Global email service instance
_email_service = None


def get_email_service() -> EmailService:
    """Get global email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
