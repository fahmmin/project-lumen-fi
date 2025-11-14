"""
PROJECT LUMEN - Financial Health Score Agent
Calculates overall financial health score (0-100)
"""

from typing import Dict
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

from backend.utils.user_storage import get_user_storage
from backend.agents.personal_finance_agent import get_personal_finance_agent
from backend.utils.logger import logger


class HealthScoreAgent:
    """Calculates financial health score"""

    def __init__(self):
        self.user_storage = get_user_storage()
        self.finance_agent = get_personal_finance_agent()

    def calculate_score(self, user_id: str) -> Dict:
        """
        Calculate financial health score

        Args:
            user_id: User ID

        Returns:
            Health score breakdown
        """
        logger.info(f"HealthScoreAgent: Calculating score for {user_id}")

        # Get user profile (auto-create if doesn't exist)
        profile = self.user_storage.ensure_profile_exists(user_id)

        # Get dashboard data
        try:
            dashboard = self.finance_agent.analyze_dashboard(user_id, "month")
        except:
            dashboard = None

        # Calculate each component
        debt_score = self._calculate_debt_score(user_id, profile, dashboard)
        emergency_score = self._calculate_emergency_fund_score(user_id, profile, dashboard)
        savings_score = self._calculate_savings_rate_score(dashboard)
        volatility_score = self._calculate_volatility_score(user_id)
        goal_score = self._calculate_goal_progress_score(user_id)

        # Total score
        total_score = (
            debt_score['score'] +
            emergency_score['score'] +
            savings_score['score'] +
            volatility_score['score'] +
            goal_score['score']
        )

        # Determine rating
        if total_score >= 80:
            rating = "Excellent"
        elif total_score >= 70:
            rating = "Good"
        elif total_score >= 60:
            rating = "Fair"
        else:
            rating = "Needs Improvement"

        # Generate recommendations
        recommendations = []
        if emergency_score['score'] < emergency_score['max'] * 0.7:
            recommendations.append(
                f"Build emergency fund to {emergency_score['target_months']} months of expenses"
            )
        if savings_score['score'] < savings_score['max'] * 0.7:
            recommendations.append("Increase your savings rate to at least 15%")
        if volatility_score['score'] < volatility_score['max'] * 0.7:
            recommendations.append("Reduce spending volatility by creating a stricter budget")
        if goal_score['score'] < goal_score['max'] * 0.7:
            recommendations.append("Increase goal contributions to stay on track")

        return {
            "user_id": user_id,
            "health_score": int(total_score),
            "rating": rating,
            "updated_at": date.today().isoformat(),
            "breakdown": {
                "debt_to_income": debt_score,
                "emergency_fund": emergency_score,
                "savings_rate": savings_score,
                "spending_volatility": volatility_score,
                "goal_progress": goal_score
            },
            "recommendations": recommendations
        }

    # ==================== SCORE COMPONENTS ====================

    def _calculate_debt_score(self, user_id: str, profile, dashboard) -> Dict:
        """Calculate debt-to-income ratio score (max 25 points)"""
        # For now, assume no debt (would need debt tracking)
        # TODO: Integrate with debt data when available

        # Placeholder: assume good debt situation
        debt_to_income = 0.15  # 15% - example
        max_score = 25

        if debt_to_income <= 0.15:
            score = max_score
            rating = "excellent"
        elif debt_to_income <= 0.30:
            score = max_score * 0.8
            rating = "good"
        elif debt_to_income <= 0.43:
            score = max_score * 0.6
            rating = "fair"
        else:
            score = max_score * 0.4
            rating = "poor"

        return {
            "score": int(score),
            "max": max_score,
            "value": debt_to_income,
            "rating": rating,
            "description": f"{debt_to_income*100:.0f}% debt-to-income ratio is {rating}"
        }

    def _calculate_emergency_fund_score(self, user_id: str, profile, dashboard) -> Dict:
        """Calculate emergency fund adequacy score (max 25 points)"""
        max_score = 25

        if not dashboard:
            return {"score": 0, "max": max_score, "rating": "unknown"}

        monthly_expenses = dashboard['summary']['total_spent']

        # Get all user goals, check for emergency fund
        goals = self.user_storage.list_goals(user_id)
        emergency_fund = 0.0

        for goal in goals:
            if 'emergency' in goal.name.lower():
                emergency_fund = goal.current_savings
                break

        if monthly_expenses > 0:
            months_covered = emergency_fund / monthly_expenses
        else:
            months_covered = 0

        target_months = 6  # Ideal: 6 months of expenses

        if months_covered >= 6:
            score = max_score
            rating = "excellent"
        elif months_covered >= 3:
            score = max_score * 0.72
            rating = "good"
        elif months_covered >= 1:
            score = max_score * 0.45
            rating = "fair"
        else:
            score = max_score * 0.2
            rating = "poor"

        target_amount = monthly_expenses * target_months

        return {
            "score": int(score),
            "max": max_score,
            "value": emergency_fund,
            "months_covered": round(months_covered, 1),
            "target_months": target_months,
            "target_amount": round(target_amount, 2),
            "rating": rating,
            "description": f"Emergency fund covers {months_covered:.1f} months of expenses (target: 3-6 months)"
        }

    def _calculate_savings_rate_score(self, dashboard) -> Dict:
        """Calculate savings rate score (max 20 points)"""
        max_score = 20

        if not dashboard:
            return {"score": 0, "max": max_score, "rating": "unknown"}

        savings_rate = dashboard['summary']['savings_rate']

        if savings_rate >= 0.20:  # 20%+
            score = max_score
            rating = "excellent"
        elif savings_rate >= 0.15:  # 15-20%
            score = max_score * 0.8
            rating = "good"
        elif savings_rate >= 0.10:  # 10-15%
            score = max_score * 0.6
            rating = "fair"
        elif savings_rate >= 0.05:  # 5-10%
            score = max_score * 0.4
            rating = "fair"
        else:
            score = max_score * 0.2
            rating = "poor"

        return {
            "score": int(score),
            "max": max_score,
            "value": savings_rate,
            "rating": rating,
            "description": f"{savings_rate*100:.0f}% savings rate is {rating}"
        }

    def _calculate_volatility_score(self, user_id: str) -> Dict:
        """Calculate spending volatility score (max 15 points)"""
        max_score = 15

        # Get last 6 months spending
        try:
            end_date = date.today()
            monthly_totals = []

            for i in range(6):
                month_start = end_date - relativedelta(months=i+1)
                month_end = end_date - relativedelta(months=i)
                dashboard = self.finance_agent.analyze_dashboard(user_id, "month")
                monthly_totals.append(dashboard['summary']['total_spent'])

            if len(monthly_totals) < 3:
                return {"score": max_score // 2, "max": max_score, "rating": "unknown"}

            # Calculate coefficient of variation
            mean = np.mean(monthly_totals)
            std = np.std(monthly_totals)

            if mean > 0:
                volatility = std / mean
            else:
                volatility = 0

            # Lower volatility = higher score
            if volatility <= 0.10:  # 10% or less
                score = max_score
                rating = "excellent"
            elif volatility <= 0.20:  # 10-20%
                score = max_score * 0.7
                rating = "good"
            elif volatility <= 0.30:  # 20-30%
                score = max_score * 0.5
                rating = "moderate"
            else:
                score = max_score * 0.3
                rating = "high"

            return {
                "score": int(score),
                "max": max_score,
                "value": round(volatility, 2),
                "rating": rating,
                "description": f"Spending varies by {volatility*100:.0f}% month-to-month"
            }

        except:
            return {"score": max_score // 2, "max": max_score, "rating": "unknown"}

    def _calculate_goal_progress_score(self, user_id: str) -> Dict:
        """Calculate goal progress score (max 15 points)"""
        max_score = 15

        goals = self.user_storage.list_goals(user_id)

        if not goals:
            return {
                "score": max_score // 2,
                "max": max_score,
                "value": 0,
                "rating": "no_goals",
                "description": "No financial goals set"
            }

        # Count goals on track
        on_track = 0
        total = len(goals)

        for goal in goals:
            # Simple check: if progress > 10%, consider on track
            if goal.progress_percentage > 10 or goal.status.value == "on_track":
                on_track += 1

        progress_ratio = on_track / total if total > 0 else 0

        if progress_ratio >= 0.75:  # 75%+ on track
            score = max_score
            rating = "excellent"
        elif progress_ratio >= 0.50:  # 50-75%
            score = max_score * 0.7
            rating = "good"
        elif progress_ratio >= 0.25:  # 25-50%
            score = max_score * 0.5
            rating = "fair"
        else:
            score = max_score * 0.3
            rating = "poor"

        return {
            "score": int(score),
            "max": max_score,
            "value": progress_ratio,
            "on_track": on_track,
            "total_goals": total,
            "rating": rating,
            "description": f"On track with {on_track} of {total} goals"
        }


# Global agent instance
_health_score_agent = None


def get_health_score_agent() -> HealthScoreAgent:
    """Get global health score agent instance"""
    global _health_score_agent
    if _health_score_agent is None:
        _health_score_agent = HealthScoreAgent()
    return _health_score_agent
