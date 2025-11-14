"""
PROJECT LUMEN - Goal Planner Agent
Creates savings and investment plans for financial goals
"""

from typing import Dict, List
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from backend.utils.user_storage import get_user_storage
from backend.utils.investment_calculator import InvestmentCalculator
from backend.agents.personal_finance_agent import get_personal_finance_agent
from backend.utils.logger import logger


class GoalPlannerAgent:
    """Creates and tracks financial goal plans"""

    def __init__(self):
        self.user_storage = get_user_storage()
        self.calculator = InvestmentCalculator()
        self.finance_agent = get_personal_finance_agent()

    def create_plan(self, goal_id: str, user_id: str) -> Dict:
        """
        Create savings and investment plan for goal

        Args:
            goal_id: Goal ID
            user_id: User ID

        Returns:
            Complete savings plan
        """
        logger.info(f"GoalPlannerAgent: Creating plan for goal {goal_id}")

        # Get goal
        goal = self.user_storage.get_goal(goal_id, user_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        # Get user profile (auto-create if doesn't exist)
        profile = self.user_storage.ensure_profile_exists(user_id)

        # Calculate months remaining
        today = date.today()
        months_remaining = (
            (goal.target_date.year - today.year) * 12 +
            (goal.target_date.month - today.month)
        )

        if months_remaining <= 0:
            return {
                "goal_id": goal_id,
                "message": "Goal date has passed or is today",
                "status": "expired"
            }

        # Get current savings rate from recent spending
        try:
            dashboard = self.finance_agent.analyze_dashboard(user_id, "month")
            current_savings_monthly = dashboard['summary']['savings']
        except:
            current_savings_monthly = 0.0

        # Calculate amount needed
        amount_needed = goal.target_amount - goal.current_savings

        # Determine time horizon and risk
        years_remaining = months_remaining / 12
        risk_tolerance = self._determine_risk_tolerance(years_remaining)

        # Get asset allocation
        allocation = self.calculator.recommend_asset_allocation(
            years_remaining,
            risk_tolerance
        )

        # Estimate expected return
        expected_return = self.calculator.estimate_expected_return(allocation)

        # Calculate monthly savings needed
        monthly_savings_required = self.calculator.calculate_monthly_savings_needed(
            goal.target_amount,
            goal.current_savings,
            months_remaining,
            expected_return
        )

        # Calculate gap
        gap = monthly_savings_required - current_savings_monthly

        # Generate recommendations
        recommendations = self._generate_recommendations(
            user_id,
            gap,
            profile.salary_monthly
        )

        # Create milestones
        milestones = self.calculator.create_milestones(
            today,
            goal.target_date,
            goal.target_amount,
            goal.current_savings
        )

        # Project final amount
        projected_final = self.calculator.project_future_value(
            goal.current_savings,
            monthly_savings_required,
            months_remaining,
            expected_return
        )

        return {
            "goal_id": goal_id,
            "goal_name": goal.name,
            "target_amount": goal.target_amount,
            "target_date": goal.target_date.isoformat(),
            "months_remaining": months_remaining,
            "current_savings": goal.current_savings,
            "amount_needed": round(amount_needed, 2),
            "plan": {
                "monthly_savings_required": round(monthly_savings_required, 2),
                "current_savings_rate": round(current_savings_monthly, 2),
                "gap": round(gap, 2),
                "recommendations": recommendations
            },
            "investment_strategy": {
                "time_horizon": f"{years_remaining:.1f} years",
                "risk_level": allocation['risk_level'],
                "asset_allocation": allocation,
                "expected_return": round(expected_return * 100, 1),
                "projected_final_amount": round(projected_final, 2),
                "rationale": self._get_allocation_rationale(years_remaining, allocation)
            },
            "milestones": milestones
        }

    def track_progress(self, goal_id: str, user_id: str) -> Dict:
        """
        Track progress toward goal

        Args:
            goal_id: Goal ID
            user_id: User ID

        Returns:
            Progress tracking data
        """
        goal = self.user_storage.get_goal(goal_id, user_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        # Calculate expected savings by now
        today = date.today()
        months_since_creation = (
            (today.year - goal.created_at.year) * 12 +
            (today.month - goal.created_at.month)
        )

        total_months = (
            (goal.target_date.year - goal.created_at.year) * 12 +
            (goal.target_date.month - goal.created_at.month)
        )

        if total_months <= 0:
            expected_progress = 100
        else:
            expected_progress = (months_since_creation / total_months) * 100

        actual_progress = goal.progress_percentage

        # Determine if on track
        on_track = actual_progress >= (expected_progress * 0.9)  # Within 10%

        # Estimate completion date based on current rate
        if months_since_creation > 0 and goal.current_savings > 0:
            monthly_contribution_avg = goal.current_savings / months_since_creation
            remaining_amount = goal.target_amount - goal.current_savings

            if monthly_contribution_avg > 0:
                months_to_completion = remaining_amount / monthly_contribution_avg
                projected_completion = today + relativedelta(months=int(months_to_completion))
            else:
                projected_completion = None
        else:
            projected_completion = goal.target_date
            monthly_contribution_avg = 0

        # Calculate if ahead or behind
        if projected_completion and projected_completion < goal.target_date:
            days_ahead = (goal.target_date - projected_completion).days
            ahead_behind = f"{days_ahead // 7} weeks ahead of schedule"
        elif projected_completion and projected_completion > goal.target_date:
            days_behind = (projected_completion - goal.target_date).days
            ahead_behind = f"{days_behind // 7} weeks behind schedule"
        else:
            ahead_behind = "On schedule"

        # Generate adjustments needed
        months_remaining = (
            (goal.target_date.year - today.year) * 12 +
            (goal.target_date.month - today.month)
        )

        if months_remaining > 0:
            required_monthly = (goal.target_amount - goal.current_savings) / months_remaining
        else:
            required_monthly = 0

        adjustments = []
        if monthly_contribution_avg < required_monthly:
            shortfall = required_monthly - monthly_contribution_avg
            adjustments.append(
                f"You're saving ${monthly_contribution_avg:.2f}/month but need ${required_monthly:.2f}/month"
            )
            adjustments.append(
                f"Increase monthly savings by ${shortfall:.2f} to stay on track"
            )
        else:
            adjustments.append("You're on track! Keep up the good work.")

        return {
            "goal_id": goal_id,
            "goal_name": goal.name,
            "progress_percentage": round(actual_progress, 1),
            "current_savings": goal.current_savings,
            "target_amount": goal.target_amount,
            "on_track": on_track,
            "projected_completion_date": projected_completion.isoformat() if projected_completion else None,
            "target_date": goal.target_date.isoformat(),
            "ahead_behind": ahead_behind,
            "monthly_contribution_avg": round(monthly_contribution_avg, 2),
            "required_monthly_contribution": round(required_monthly, 2),
            "adjustments_needed": adjustments
        }

    # ==================== HELPER METHODS ====================

    def _determine_risk_tolerance(self, years: float) -> str:
        """Determine risk tolerance based on time horizon"""
        if years < 2:
            return "conservative"
        elif years < 5:
            return "moderate"
        else:
            return "moderate"  # Default to moderate

    def _generate_recommendations(
        self,
        user_id: str,
        gap: float,
        salary: float
    ) -> List[str]:
        """Generate recommendations to close savings gap"""
        recommendations = []

        if gap <= 0:
            recommendations.append("You're already saving enough to meet your goal!")
            recommendations.append("Consider increasing your goal target or saving more for other goals.")
            return recommendations

        # Get recent spending to find areas to cut
        try:
            dashboard = self.finance_agent.analyze_dashboard(user_id, "month")
            spending = dashboard['spending_by_category']
            vs_budget = dashboard['vs_budget']

            # Find overspending categories
            overspending = [
                (cat, data['difference'])
                for cat, data in vs_budget.items()
                if data['status'] == 'over'
            ]

            overspending.sort(key=lambda x: abs(x[1]), reverse=True)

            total_reduction_found = 0
            for category, over_amount in overspending[:3]:
                if total_reduction_found >= gap:
                    break

                reduction = min(abs(over_amount), gap - total_reduction_found)
                actual = vs_budget[category]['actual']
                new_target = actual - reduction

                recommendations.append(
                    f"Reduce {category} from ${actual:.2f} to ${new_target:.2f} (saves ${reduction:.2f}/month)"
                )
                total_reduction_found += reduction

            # If still short, suggest other areas
            if total_reduction_found < gap:
                remaining_gap = gap - total_reduction_found

                # Suggest subscription review
                if 'entertainment' in spending or 'subscriptions' in spending:
                    recommendations.append(
                        f"Review subscriptions to save ${min(remaining_gap, 100):.2f}/month"
                    )
                    total_reduction_found += min(remaining_gap, 100)

                # Suggest dining out reduction
                if 'dining' in spending and total_reduction_found < gap:
                    dining_amount = spending['dining']['amount']
                    reduction = min(dining_amount * 0.3, gap - total_reduction_found)
                    recommendations.append(
                        f"Reduce dining out to save ${reduction:.2f}/month"
                    )

            recommendations.append(f"Total adjustments needed: ${gap:.2f}/month")

        except Exception as e:
            logger.warning(f"Could not generate detailed recommendations: {e}")
            recommendations.append(f"Find ways to reduce spending by ${gap:.2f}/month")
            recommendations.append("Review your largest expense categories for potential savings")

        return recommendations

    def _get_allocation_rationale(self, years: float, allocation: Dict) -> str:
        """Get rationale for asset allocation"""
        if years < 1:
            return "Very short time horizon requires capital preservation. Focus on cash and bonds."
        elif years < 3:
            return f"{years:.0f}-year horizon allows moderate risk. {allocation['stocks']}% stocks provides some growth with stability."
        elif years < 5:
            return f"{years:.0f}-year horizon allows moderate risk. {allocation['stocks']}/{allocation['bonds']} stock/bond allocation balances growth with stability."
        elif years < 10:
            return f"{years:.0f}-year horizon allows growth focus. {allocation['stocks']}% stocks maximizes long-term returns."
        else:
            return f"{years:.0f}-year horizon allows aggressive growth. {allocation['stocks']}% stocks capitalizes on long-term market growth."


# Global agent instance
_goal_planner_agent = None


def get_goal_planner_agent() -> GoalPlannerAgent:
    """Get global goal planner agent instance"""
    global _goal_planner_agent
    if _goal_planner_agent is None:
        _goal_planner_agent = GoalPlannerAgent()
    return _goal_planner_agent
