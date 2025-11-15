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
from backend.utils.ollama_client import ollama_client
from backend.utils.logger import logger


class GoalPlannerAgent:
    """Creates and tracks financial goal plans"""

    def __init__(self):
        self.user_storage = get_user_storage()
        self.calculator = InvestmentCalculator()
        self.finance_agent = get_personal_finance_agent()
        self.ollama = ollama_client

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

    def analyze_receipt_impact_on_goals(
        self,
        user_id: str,
        receipt: Dict
    ) -> Dict:
        """
        Analyze how a single receipt impacts user's goals using LLM

        Args:
            user_id: User ID
            receipt: Receipt data with vendor, amount, category

        Returns:
            Goal impact analysis with LLM-generated insights
        """
        logger.info(f"GoalPlannerAgent: Analyzing receipt impact on goals - {receipt.get('vendor')}")

        # Get user's active goals
        goals = self.user_storage.get_all_goals(user_id)
        active_goals = [g for g in goals if g.status in ["on_track", "behind"]]

        if not active_goals:
            return {
                "has_goals": False,
                "message": "No active goals to analyze impact",
                "receipt_amount": receipt.get('amount', 0)
            }

        # Get user profile
        profile = self.user_storage.ensure_profile_exists(user_id)

        # Format goals for LLM
        goals_summary = "\n".join([
            f"- {g.name}: ${g.current_savings:.2f} / ${g.target_amount:.2f} (target: {g.target_date})"
            for g in active_goals
        ])

        # Calculate current savings rate
        try:
            dashboard = self.finance_agent.analyze_dashboard(user_id, "month")
            current_savings = dashboard['summary']['savings']
        except:
            current_savings = 0

        prompt = f"""Analyze how this purchase impacts the user's financial goals.

Purchase Details:
- Vendor: {receipt.get('vendor', 'Unknown')}
- Amount: ${receipt.get('amount', 0):.2f}
- Category: {receipt.get('category', 'other')}

User Financial Situation:
- Monthly Income: ${profile.salary_monthly:.2f}
- Current Monthly Savings: ${current_savings:.2f}

Active Goals:
{goals_summary}

Analyze the impact of this purchase on the user's goals:
1. Does this purchase delay any goals? By how much (days/weeks)?
2. Which specific goal is most affected?
3. What's the opportunity cost (what could this money have contributed to)?
4. Is this purchase discretionary or necessary?
5. Specific recommendation to stay on track

Respond in JSON format:
{{
    "affects_goals": true/false,
    "most_affected_goal": "goal name or null",
    "delay_estimate": "X days/weeks or null",
    "opportunity_cost": "specific description",
    "is_discretionary": true/false,
    "impact_level": "high/medium/low/none",
    "recommendation": "specific actionable advice",
    "alternative_action": "what user could do instead"
}}

Return ONLY valid JSON."""

        system_message = "You are a financial coach who helps people understand how their spending affects their goals. Be specific and encouraging."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=600
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                return self._fallback_goal_impact(receipt, active_goals, current_savings)

            return {
                "receipt": {
                    "vendor": receipt.get('vendor'),
                    "amount": receipt.get('amount'),
                    "category": receipt.get('category')
                },
                "active_goals_count": len(active_goals),
                "impact_analysis": result,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in LLM goal impact analysis: {e}")
            return self._fallback_goal_impact(receipt, active_goals, current_savings)

    def suggest_goal_aligned_spending(
        self,
        user_id: str,
        planned_amount: float,
        category: str
    ) -> Dict:
        """
        Before a purchase, check if it aligns with goals using LLM

        Args:
            user_id: User ID
            planned_amount: Amount user plans to spend
            category: Spending category

        Returns:
            Recommendation on whether to proceed with purchase
        """
        logger.info(f"GoalPlannerAgent: Checking planned purchase of ${planned_amount:.2f} in {category}")

        # Get user's active goals
        goals = self.user_storage.get_all_goals(user_id)
        active_goals = [g for g in goals if g.status in ["on_track", "behind"]]

        if not active_goals:
            return {
                "has_goals": False,
                "recommendation": "proceed",
                "message": "No active goals to consider"
            }

        # Get user profile and current spending
        profile = self.user_storage.ensure_profile_exists(user_id)

        try:
            dashboard = self.finance_agent.analyze_dashboard(user_id, "month")
            spent_in_category = dashboard['spending_by_category'].get(category, {}).get('amount', 0)
            budget_for_category = profile.budget_categories.get(category, 0)
        except:
            spent_in_category = 0
            budget_for_category = profile.budget_categories.get(category, 0)

        # Format goals
        goals_summary = "\n".join([
            f"- {g.name}: ${g.current_savings:.2f} / ${g.target_amount:.2f} (target: {g.target_date})"
            for g in active_goals
        ])

        prompt = f"""The user is about to make a purchase. Should they proceed given their financial goals?

Planned Purchase:
- Amount: ${planned_amount:.2f}
- Category: {category}

Current Financial Situation:
- Monthly Income: ${profile.salary_monthly:.2f}
- Already spent in {category} this month: ${spent_in_category:.2f}
- Budget for {category}: ${budget_for_category:.2f}

Active Goals:
{goals_summary}

Provide a recommendation:
1. Should they proceed, delay, or skip this purchase?
2. Why (specific reason related to their goals)?
3. Alternative action if they should delay/skip
4. Impact on goals if they proceed

Respond in JSON format:
{{
    "recommendation": "proceed/delay/skip",
    "reasoning": "specific reason tied to goals and budget",
    "alternative": "specific alternative action",
    "impact_if_proceed": "what happens to goals if they buy",
    "confidence": "high/medium/low"
}}

Return ONLY valid JSON."""

        system_message = "You are a financial advisor who helps people make spending decisions aligned with their goals."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=500
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                return {"recommendation": "review", "message": "Unable to analyze at this time"}

            return {
                "planned_purchase": {
                    "amount": planned_amount,
                    "category": category
                },
                "analysis": result,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in goal-aligned spending suggestion: {e}")
            return {"recommendation": "review", "error": str(e)}

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

    def _fallback_goal_impact(self, receipt: Dict, goals: List, current_savings: float) -> Dict:
        """Fallback goal impact analysis when LLM fails"""
        amount = receipt.get('amount', 0)
        category = receipt.get('category', 'other')

        # Simple rule-based analysis
        is_discretionary = category in ['dining', 'entertainment', 'shopping']
        impact_level = "high" if amount > 100 and is_discretionary else "low"

        return {
            "receipt": {
                "vendor": receipt.get('vendor'),
                "amount": amount,
                "category": category
            },
            "active_goals_count": len(goals),
            "impact_analysis": {
                "affects_goals": is_discretionary and amount > 50,
                "most_affected_goal": goals[0].name if goals else None,
                "delay_estimate": "Minimal delay" if amount < 100 else "Could delay goals",
                "opportunity_cost": f"${amount:.2f} could have gone toward your goals",
                "is_discretionary": is_discretionary,
                "impact_level": impact_level,
                "recommendation": "Review necessity of this expense" if is_discretionary else "Essential expense",
                "alternative_action": "Consider saving instead" if is_discretionary else "N/A"
            },
            "analyzed_at": datetime.now().isoformat()
        }


# Global agent instance
_goal_planner_agent = None


def get_goal_planner_agent() -> GoalPlannerAgent:
    """Get global goal planner agent instance"""
    global _goal_planner_agent
    if _goal_planner_agent is None:
        _goal_planner_agent = GoalPlannerAgent()
    return _goal_planner_agent
