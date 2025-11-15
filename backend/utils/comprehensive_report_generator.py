"""
Comprehensive Report Generator for Agentic RAG Reports
Generates detailed PDF/HTML reports with all agent insights
"""

from typing import Dict, Optional
import os
import uuid
from datetime import datetime
from pathlib import Path
from backend.utils.logger import logger
from backend.config import settings


class ComprehensiveReportGenerator:
    """Generates comprehensive financial reports with all agentic insights"""

    def __init__(self):
        self.output_dir = settings.REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_comprehensive_report(
        self,
        report_data: Dict,
        format: str = "html"
    ) -> Path:
        """
        Generate comprehensive financial report

        Args:
            report_data: Complete report data from AgenticReportGenerator
            format: "pdf" or "html" (default: html)

        Returns:
            Path to generated report file
        """
        try:
            if format == "pdf":
                try:
                    return await self._generate_pdf_report(report_data)
                except ImportError:
                    logger.warning("ReportLab not available, falling back to HTML")
                    return await self._generate_html_report(report_data)
            else:
                return await self._generate_html_report(report_data)

        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            raise

    async def _generate_html_report(self, report_data: Dict) -> Path:
        """Generate comprehensive HTML report"""

        metadata = report_data.get("report_metadata", {})
        executive_summary = report_data.get("executive_summary", {})
        financial_overview = report_data.get("financial_overview", {})
        goal_progress = report_data.get("goal_progress", {})
        savings_opportunities = report_data.get("savings_opportunities", {})
        fraud_alerts = report_data.get("fraud_alerts", {})
        spending_patterns = report_data.get("spending_patterns", {})
        behavioral_insights = report_data.get("behavioral_insights", {})
        compliance_status = report_data.get("compliance_status", {})
        audit_summary = report_data.get("audit_summary", {})
        recommendations = report_data.get("recommendations", [])

        # Create filename
        user_id = metadata.get("user_id", "unknown")
        report_type = metadata.get("report_type", "report")
        report_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_report_{user_id}_{timestamp}_{report_id}.html"
        filepath = self.output_dir / filename

        # Build HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROJECT LUMEN - Comprehensive Financial Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
        }}

        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 18px;
            opacity: 0.9;
        }}

        .metadata {{
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 2px solid #e9ecef;
        }}

        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .metadata-item {{
            display: flex;
            flex-direction: column;
        }}

        .metadata-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metadata-value {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-top: 5px;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 40px;
            page-break-inside: avoid;
        }}

        .section-title {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
        }}

        .section-title .icon {{
            margin-right: 10px;
            font-size: 28px;
        }}

        .health-score {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }}

        .health-score-value {{
            font-size: 72px;
            font-weight: bold;
            margin: 20px 0;
        }}

        .health-score-label {{
            font-size: 20px;
            opacity: 0.9;
        }}

        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .stat-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}

        .stat-subvalue {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}

        .alert {{
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: flex;
            align-items: start;
        }}

        .alert.critical {{
            background: #fff3f3;
            border-left: 5px solid #dc3545;
        }}

        .alert.warning {{
            background: #fff8e1;
            border-left: 5px solid #ffc107;
        }}

        .alert.info {{
            background: #e3f2fd;
            border-left: 5px solid #2196f3;
        }}

        .alert.success {{
            background: #e8f5e9;
            border-left: 5px solid #4caf50;
        }}

        .alert-icon {{
            font-size: 24px;
            margin-right: 15px;
        }}

        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .table td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        .table tr:last-child td {{
            border-bottom: none;
        }}

        .table tr:hover {{
            background: #f8f9fa;
        }}

        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 25px;
            overflow: hidden;
            margin: 10px 0;
            position: relative;
        }}

        .progress-fill {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}

        .recommendation-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        }}

        .recommendation-card.high {{
            border-left: 5px solid #dc3545;
        }}

        .recommendation-card.medium {{
            border-left: 5px solid #ffc107;
        }}

        .recommendation-card.low {{
            border-left: 5px solid #17a2b8;
        }}

        .recommendation-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}

        .recommendation-description {{
            color: #666;
            margin-bottom: 10px;
        }}

        .recommendation-action {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            font-style: italic;
            color: #555;
        }}

        .highlight-box {{
            background: linear-gradient(135deg, #fff8e1 0%, #ffe082 100%);
            border-left: 5px solid #ffc107;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            color: #666;
            font-size: 14px;
            border-top: 2px solid #e9ecef;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .report-container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- Header -->
        <div class="header">
            <h1>💰 PROJECT LUMEN</h1>
            <div class="subtitle">Comprehensive Financial Intelligence Report</div>
        </div>

        <!-- Metadata -->
        <div class="metadata">
            <div class="metadata-grid">
                <div class="metadata-item">
                    <span class="metadata-label">Report Period</span>
                    <span class="metadata-value">{metadata.get('period', 'N/A')}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Report Type</span>
                    <span class="metadata-value">{metadata.get('report_type', 'N/A').title()}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Generated</span>
                    <span class="metadata-value">{datetime.fromisoformat(metadata.get('generated_at', datetime.now().isoformat())).strftime('%b %d, %Y %I:%M %p')}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">User ID</span>
                    <span class="metadata-value">{user_id[:16]}...</span>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="content">
"""

        # Executive Summary with Health Score
        health_score = executive_summary.get("financial_health_score", 0)
        html_content += f"""
            <!-- Executive Summary -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">📊</span>
                    Executive Summary
                </h2>

                <div class="health-score">
                    <div class="health-score-label">Financial Health Score</div>
                    <div class="health-score-value">{health_score:.0f}/100</div>
                    <div class="health-score-label">
                        {'Excellent' if health_score >= 80 else 'Good' if health_score >= 60 else 'Fair' if health_score >= 40 else 'Needs Improvement'}
                    </div>
                </div>

                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Spending</div>
                        <div class="stat-value">${executive_summary.get('total_spending', 0):,.2f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Budget Usage</div>
                        <div class="stat-value">{executive_summary.get('budget_usage_percentage', 0):.1f}%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Active Goals</div>
                        <div class="stat-value">{executive_summary.get('active_goals', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Potential Savings</div>
                        <div class="stat-value">${executive_summary.get('potential_savings', 0):,.2f}</div>
                    </div>
                </div>

                <h3 style="margin-top: 30px; margin-bottom: 15px;">Key Highlights</h3>
"""

        # Key highlights
        for highlight in executive_summary.get("key_highlights", []):
            alert_type = highlight.get("type", "info")
            message = highlight.get("message", "")
            icons = {"warning": "⚠️", "opportunity": "💡", "alert": "🚨", "info": "ℹ️"}
            icon = icons.get(alert_type, "ℹ️")

            html_content += f"""
                <div class="alert {alert_type}">
                    <span class="alert-icon">{icon}</span>
                    <div>{message}</div>
                </div>
"""

        html_content += """
            </div>
"""

        # Financial Overview
        html_content += f"""
            <!-- Financial Overview -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">💳</span>
                    Financial Overview
                </h2>

                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Spending</div>
                        <div class="stat-value">${financial_overview.get('total_spending', 0):,.2f}</div>
                        <div class="stat-subvalue">Trend: {financial_overview.get('spending_trend', 'stable').title()}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Monthly Average</div>
                        <div class="stat-value">${financial_overview.get('monthly_average', 0):,.2f}</div>
                    </div>
                </div>
"""

        # Budget status
        budget_status = financial_overview.get("budget_status", {})
        if budget_status:
            budget_total = budget_status.get("total_budget", 0)
            budget_used = budget_status.get("used", 0)
            budget_percentage = (budget_used / budget_total * 100) if budget_total > 0 else 0

            html_content += f"""
                <h3 style="margin-top: 25px;">Budget Status</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(100, budget_percentage):.1f}%;">
                        {budget_percentage:.1f}%
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                    <span>${budget_used:,.2f} used</span>
                    <span>${budget_total - budget_used:,.2f} remaining</span>
                </div>
"""

        # Top categories
        top_categories = financial_overview.get("top_categories", [])
        if top_categories:
            html_content += """
                <h3 style="margin-top: 25px;">Top Spending Categories</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Amount</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            total_spending = financial_overview.get('total_spending', 1)
            for cat in top_categories[:5]:
                if isinstance(cat, dict):
                    category = cat.get('category', 'Unknown')
                    amount = cat.get('amount', 0)
                    percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                    html_content += f"""
                        <tr>
                            <td>{category}</td>
                            <td>${amount:,.2f}</td>
                            <td>{percentage:.1f}%</td>
                        </tr>
"""
            html_content += """
                    </tbody>
                </table>
"""

        html_content += """
            </div>
"""

        # Goal Progress
        goals = goal_progress.get("goals", [])
        if goals:
            html_content += f"""
            <!-- Goal Progress -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">🎯</span>
                    Goal Progress
                </h2>

                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-label">Active Goals</div>
                        <div class="stat-value">{goal_progress.get('active_goals', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Completed Goals</div>
                        <div class="stat-value">{goal_progress.get('completed_goals', 0)}</div>
                    </div>
                </div>

                <table class="table" style="margin-top: 20px;">
                    <thead>
                        <tr>
                            <th>Goal Name</th>
                            <th>Progress</th>
                            <th>Amount</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for goal in goals[:5]:
                goal_name = goal.get("name", "Unknown Goal")
                progress_pct = goal.get("progress_percentage", 0)
                current = goal.get("current", 0)
                target = goal.get("target", 0)
                status = goal.get("status", "unknown")
                status_color = "green" if status == "on_track" else "orange"

                html_content += f"""
                        <tr>
                            <td><strong>{goal_name}</strong></td>
                            <td>
                                <div class="progress-bar" style="height: 20px;">
                                    <div class="progress-fill" style="width: {min(100, progress_pct):.1f}%;">
                                        {progress_pct:.1f}%
                                    </div>
                                </div>
                            </td>
                            <td>${current:,.2f} / ${target:,.2f}</td>
                            <td style="color: {status_color}; font-weight: 600;">{status.replace('_', ' ').title()}</td>
                        </tr>
"""
            html_content += """
                    </tbody>
                </table>
            </div>
"""

        # Savings Opportunities
        opportunities = savings_opportunities.get("opportunities", [])
        if opportunities:
            html_content += f"""
            <!-- Savings Opportunities -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">💡</span>
                    Savings Opportunities
                </h2>

                <div class="highlight-box">
                    <h3>Potential Savings: ${savings_opportunities.get('total_potential_savings', 0):,.2f}</h3>
                    <p>We've identified {savings_opportunities.get('opportunities_found', 0)} opportunities to save money.</p>
                </div>

                <div style="margin-top: 20px;">
"""
            for opp in opportunities[:5]:
                title = opp.get("title", "Savings Opportunity")
                description = opp.get("description", "")
                potential = opp.get("potential_savings", 0)

                html_content += f"""
                    <div class="alert success">
                        <span class="alert-icon">💰</span>
                        <div>
                            <strong>{title}</strong>
                            <p style="margin: 5px 0;">{description}</p>
                            <p style="color: #4caf50; font-weight: 600;">Potential savings: ${potential:,.2f}</p>
                        </div>
                    </div>
"""
            html_content += """
                </div>
            </div>
"""

        # Fraud Alerts
        fraud_alert_list = fraud_alerts.get("alerts", [])
        if fraud_alert_list:
            html_content += f"""
            <!-- Fraud & Security Alerts -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">🚨</span>
                    Security & Fraud Alerts
                </h2>

                <div class="alert warning">
                    <span class="alert-icon">⚠️</span>
                    <div>
                        <strong>{fraud_alerts.get('anomalies_detected', 0)} anomalies detected</strong>
                        <p>Please review the following transactions for suspicious activity.</p>
                    </div>
                </div>

                <div style="margin-top: 20px;">
"""
            for alert in fraud_alert_list[:5]:
                alert_msg = alert.get("message", "Suspicious activity detected")
                html_content += f"""
                    <div class="alert critical">
                        <span class="alert-icon">🚨</span>
                        <div>{alert_msg}</div>
                    </div>
"""
            html_content += """
                </div>
            </div>
"""

        # Spending Patterns
        recurring = spending_patterns.get("recurring_expenses", [])
        if recurring:
            html_content += f"""
            <!-- Spending Patterns -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">📈</span>
                    Spending Patterns
                </h2>

                <p style="margin-bottom: 20px;">We've detected {spending_patterns.get('patterns_detected', 0)} spending patterns in your transactions.</p>

                <h3>Recurring Expenses</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Frequency</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for expense in recurring[:5]:
                desc = expense.get("description", "Recurring expense")
                freq = expense.get("frequency", "monthly")
                amount = expense.get("amount", 0)

                html_content += f"""
                        <tr>
                            <td>{desc}</td>
                            <td>{freq.title()}</td>
                            <td>${amount:,.2f}</td>
                        </tr>
"""
            html_content += """
                    </tbody>
                </table>
            </div>
"""

        # Recommendations
        if recommendations:
            html_content += """
            <!-- Recommendations -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">✨</span>
                    Personalized Recommendations
                </h2>
"""
            for rec in recommendations:
                priority = rec.get("priority", "low")
                title = rec.get("title", "Recommendation")
                description = rec.get("description", "")
                action = rec.get("action", "")

                html_content += f"""
                <div class="recommendation-card {priority}">
                    <div class="recommendation-title">{title}</div>
                    <div class="recommendation-description">{description}</div>
                    <div class="recommendation-action">
                        <strong>Action:</strong> {action}
                    </div>
                </div>
"""
            html_content += """
            </div>
"""

        # Footer
        html_content += f"""
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>PROJECT LUMEN</strong> - AI-Powered Financial Intelligence Platform</p>
            <p style="margin-top: 10px;">This report was automatically generated using advanced agentic RAG technology.</p>
            <p style="margin-top: 5px; font-size: 12px;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    </div>
</body>
</html>
"""

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Generated comprehensive HTML report: {filepath}")
        return filepath

    async def _generate_pdf_report(self, report_data: Dict) -> Path:
        """Generate comprehensive PDF report using ReportLab"""
        # TODO: Implement PDF generation with ReportLab
        # For now, fallback to HTML
        logger.warning("PDF generation not fully implemented, using HTML")
        return await self._generate_html_report(report_data)


# Global instance
_comprehensive_report_generator = None


def get_comprehensive_report_generator() -> ComprehensiveReportGenerator:
    """Get global comprehensive report generator instance"""
    global _comprehensive_report_generator
    if _comprehensive_report_generator is None:
        _comprehensive_report_generator = ComprehensiveReportGenerator()
    return _comprehensive_report_generator
