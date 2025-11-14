"""
Reports API - AI-Generated Financial Reports
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
import os

from backend.models.report import ReportRequest, ReportType
from backend.utils.pdf_generator import pdf_generator
from backend.agents.personal_finance_agent import get_personal_finance_agent
from backend.utils.user_storage import get_user_storage
from backend.utils.logger import logger

router = APIRouter(prefix="/reports", tags=["Reports & PDF Generation"])


@router.post("/generate/{user_id}")
async def generate_report(
    user_id: str,
    report_type: ReportType = Query(ReportType.MONTHLY_SUMMARY),
    period: str = Query("month", enum=["month", "quarter", "year"])
):
    """
    Generate AI-powered financial report

    **Report Types:**
    - monthly_summary: Complete financial overview
    - spending_analysis: Detailed spending breakdown
    - goal_progress: Goal tracking report
    - tax_summary: Tax-related expenses

    **Returns:**
    - Download link for generated PDF/HTML report
    """
    try:
        # Get user profile
        storage = get_user_storage()
        profile = storage.get_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        # Get financial data
        agent = get_personal_finance_agent()
        dashboard = agent.analyze_dashboard(user_id, period)
        insights = agent.get_insights(user_id)

        # Generate report
        filepath = await pdf_generator.generate_monthly_report(
            user_id=user_id,
            dashboard_data=dashboard,
            insights=insights
        )

        filename = os.path.basename(filepath)

        return {
            "success": True,
            "report_id": filename.replace('.pdf', '').replace('.html', ''),
            "user_id": user_id,
            "report_type": report_type,
            "period": period,
            "download_url": f"/reports/download/{filename}",
            "generated_at": "now",
            "message": "Report generated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download a generated report

    **Usage:**
    GET /reports/download/report_user_abc123.pdf
    """
    try:
        filepath = os.path.join("backend/data/reports", filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Report not found")

        # Determine media type
        if filename.endswith('.pdf'):
            media_type = 'application/pdf'
        elif filename.endswith('.html'):
            media_type = 'text/html'
        else:
            media_type = 'application/octet-stream'

        return FileResponse(
            path=filepath,
            media_type=media_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/history")
async def get_report_history(user_id: str, limit: int = Query(10, ge=1, le=50)):
    """
    Get user's report generation history

    **Returns:**
    List of previously generated reports with download links
    """
    try:
        reports_dir = "backend/data/reports"
        user_reports = []

        if os.path.exists(reports_dir):
            for filename in os.listdir(reports_dir):
                if filename.startswith(f"report_{user_id}_"):
                    filepath = os.path.join(reports_dir, filename)
                    file_stats = os.stat(filepath)

                    user_reports.append({
                        "filename": filename,
                        "download_url": f"/reports/download/{filename}",
                        "size_bytes": file_stats.st_size,
                        "created_at": file_stats.st_mtime,
                        "format": "PDF" if filename.endswith('.pdf') else "HTML"
                    })

        # Sort by creation time, most recent first
        user_reports.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "user_id": user_id,
            "reports": user_reports[:limit],
            "total_count": len(user_reports)
        }

    except Exception as e:
        logger.error(f"Error getting report history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
