"""
PROJECT LUMEN - Personal Finance Agent
Analyzes spending patterns, predicts future spending, and generates insights
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

from backend.rag.vector_store import get_vector_store
from backend.utils.user_storage import get_user_storage
from backend.utils.time_series import TimeSeriesForecaster
from backend.utils.ollama_client import ollama_client
from backend.utils.logger import logger


class PersonalFinanceAgent:
    """Analyzes personal finance and provides insights"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.user_storage = get_user_storage()
        self.forecaster = TimeSeriesForecaster()
        self.ollama = ollama_client

    def analyze_dashboard(self, user_id: str, period: str = "month") -> Dict:
        """
        Generate dashboard data for user

        Args:
            user_id: User ID
            period: "month", "quarter", or "year"

        Returns:
            Dashboard data with spending breakdown
        """
        logger.info(f"PersonalFinanceAgent: Generating dashboard for {user_id}")

        # Get user profile (auto-create if doesn't exist)
        profile = self.user_storage.ensure_profile_exists(user_id)

        # Get date range
        end_date = date.today()
        if period == "month":
            start_date = end_date - relativedelta(months=1)
        elif period == "quarter":
            start_date = end_date - relativedelta(months=3)
        elif period == "year":
            start_date = end_date - relativedelta(years=1)
        else:
            start_date = end_date - relativedelta(months=1)

        # Get user's receipts
        receipts = self._get_user_receipts(user_id, start_date, end_date)

        # Calculate totals
        total_spent = sum(r['amount'] for r in receipts)
        income = profile.salary_monthly

        if period == "quarter":
            income = income * 3
        elif period == "year":
            income = income * 12

        savings = income - total_spent
        savings_rate = (savings / income) if income > 0 else 0

        # Spending by category
        spending_by_category = self._calculate_category_breakdown(receipts)

        # Compare to budget
        vs_budget = self._compare_to_budget(spending_by_category, profile.budget_categories)

        # Compare to last period
        last_start = start_date - relativedelta(months=1 if period == "month" else 3)
        last_end = start_date
        last_receipts = self._get_user_receipts(user_id, last_start, last_end)
        last_total = sum(r['amount'] for r in last_receipts)

        total_change = total_spent - last_total
        percent_change = (total_change / last_total * 100) if last_total > 0 else 0

        # Generate insights
        insights = self._generate_insights(
            spending_by_category,
            vs_budget,
            percent_change,
            savings_rate
        )

        return {
            "user_id": user_id,
            "period": period,
            "month": end_date.strftime("%Y-%m") if period == "month" else None,
            "summary": {
                "income": round(income, 2),
                "total_spent": round(total_spent, 2),
                "savings": round(savings, 2),
                "savings_rate": round(savings_rate, 3)
            },
            "spending_by_category": spending_by_category,
            "vs_budget": vs_budget,
            "vs_last_period": {
                "total_change": round(total_change, 2),
                "percent_change": round(percent_change, 1),
                "trend": "increasing" if total_change > 0 else "decreasing"
            },
            "insights": insights,
            "transaction_count": len(receipts)
        }

    def get_spending_breakdown(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Get detailed spending breakdown

        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            category: Filter by category

        Returns:
            Detailed spending data
        """
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - relativedelta(months=1)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        if category:
            receipts = [r for r in receipts if r.get('category') == category]

        total_spent = sum(r['amount'] for r in receipts)
        category_breakdown = self._calculate_category_breakdown(receipts)

        return {
            "user_id": user_id,
            "period": f"{start_date} to {end_date}",
            "total_spent": round(total_spent, 2),
            "transactions": [
                {
                    "date": r['date'],
                    "vendor": r['vendor'],
                    "category": r['category'],
                    "amount": r['amount'],
                    "receipt_id": r.get('document_id')
                }
                for r in sorted(receipts, key=lambda x: x['date'], reverse=True)
            ],
            "category_breakdown": category_breakdown
        }

    def predict_spending(self, user_id: str) -> Dict:
        """
        Predict next month's spending

        Args:
            user_id: User ID

        Returns:
            Spending predictions
        """
        logger.info(f"PersonalFinanceAgent: Predicting spending for {user_id}")

        # Get last 6 months of data
        end_date = date.today()
        start_date = end_date - relativedelta(months=6)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        if len(receipts) < 10:
            return {
                "user_id": user_id,
                "prediction_for": (date.today() + relativedelta(months=1)).strftime("%Y-%m"),
                "predicted_total": 0.0,
                "confidence": "low",
                "message": "Not enough data for prediction (need at least 10 transactions)"
            }

        # Group by month
        monthly_totals = self._group_by_month(receipts)
        monthly_values = [v['total'] for v in monthly_totals.values()]

        # Overall prediction
        predicted_total, (lower, upper) = self.forecaster.simple_forecast(monthly_values)

        # Category predictions
        categories = set(r['category'] for r in receipts)
        category_predictions = {}

        for category in categories:
            pred = self.forecaster.predict_category_spending(receipts, category)
            category_predictions[category] = pred['predicted_amount']

        # Detect seasonality
        dates = [datetime.strptime(r['date'], "%Y-%m-%d").date() for r in receipts]
        seasonality = self.forecaster.detect_seasonality(
            [r['amount'] for r in receipts],
            dates
        )

        # Generate factors
        factors = []
        factors.append(f"Historical average over last {len(monthly_totals)} months")

        if seasonality['seasonal']:
            next_month = (date.today() + relativedelta(months=1)).month
            if next_month in seasonality.get('monthly_averages', {}):
                factors.append(
                    f"Seasonal trend detected (month {next_month} typically "
                    f"${seasonality['monthly_averages'][next_month]:.2f})"
                )

        # Trending up or down?
        if len(monthly_values) >= 3:
            recent_avg = np.mean(monthly_values[-3:])
            overall_avg = np.mean(monthly_values)
            if recent_avg > overall_avg * 1.1:
                factors.append("Recent spending trend is increasing")
            elif recent_avg < overall_avg * 0.9:
                factors.append("Recent spending trend is decreasing")

        return {
            "user_id": user_id,
            "prediction_for": (date.today() + relativedelta(months=1)).strftime("%Y-%m"),
            "predicted_total": round(predicted_total, 2),
            "confidence_interval": [round(lower, 2), round(upper, 2)],
            "confidence_level": 0.85,
            "breakdown_by_category": {k: round(v, 2) for k, v in category_predictions.items()},
            "factors": factors,
            "data_points": len(receipts)
        }

    def get_insights(self, user_id: str, period: str = "month") -> List[str]:
        """
        Get AI-powered spending insights for user

        Args:
            user_id: User ID
            period: Time period ("month", "quarter", or "year")

        Returns:
            List of insight strings
        """
        logger.info(f"PersonalFinanceAgent: Generating insights for {user_id}")
        
        # Get dashboard data which includes insights
        dashboard = self.analyze_dashboard(user_id, period)
        
        # Return insights from dashboard
        return dashboard.get('insights', [])

    def get_budget_recommendations(self, user_id: str) -> Dict:
        """
        Generate budget recommendations

        Args:
            user_id: User ID

        Returns:
            Budget recommendations
        """
        # Get user profile (auto-create if doesn't exist)
        profile = self.user_storage.ensure_profile_exists(user_id)

        # Get last 3 months actual spending
        end_date = date.today()
        start_date = end_date - relativedelta(months=3)
        receipts = self._get_user_receipts(user_id, start_date, end_date)

        # Calculate actual average per category
        category_totals = self._calculate_category_breakdown(receipts)

        # Average over 3 months
        actual_monthly = {
            cat: data['amount'] / 3
            for cat, data in category_totals.items()
        }

        # Current budget
        current_budget = profile.budget_categories

        # Recommended budget
        recommended_budget = {}
        rationale = {}

        for category, actual_avg in actual_monthly.items():
            budget = current_budget.get(category, 0)

            if actual_avg < budget * 0.8:
                # Spending less than budget - adjust down
                recommended_budget[category] = round(actual_avg * 1.1, 2)
                rationale[category] = f"You consistently spend less than budget - adjust to realistic level"
            elif actual_avg > budget * 1.2:
                # Overspending - suggest reduction
                recommended_budget[category] = round(budget * 1.1, 2)
                rationale[category] = f"Reduce by ${(actual_avg - budget):.2f} to meet budget goals"
            else:
                # On track
                recommended_budget[category] = budget
                rationale[category] = "Current budget is appropriate"

        # Calculate potential savings
        current_total = sum(current_budget.values())
        recommended_total = sum(recommended_budget.values())
        potential_savings = current_total - recommended_total

        return {
            "user_id": user_id,
            "current_budget": current_budget,
            "actual_spending_monthly": {k: round(v, 2) for k, v in actual_monthly.items()},
            "recommended_budget": recommended_budget,
            "rationale": rationale,
            "potential_savings": round(potential_savings, 2),
            "annual_impact": round(potential_savings * 12, 2)
        }

    def check_budget_alert_on_receipt(self, user_id: str, receipt: Dict) -> Dict:
        """
        Real-time budget alert when receipt is added - uses LLM for intelligent analysis

        Args:
            user_id: User ID
            receipt: Receipt data with vendor, amount, category

        Returns:
            Alert data with LLM-generated insights
        """
        logger.info(f"PersonalFinanceAgent: Checking budget alert for receipt - {receipt.get('vendor')}")

        profile = self.user_storage.ensure_profile_exists(user_id)
        category = receipt.get('category', 'other')
        amount = receipt.get('amount', 0)

        # Get spending so far this month
        end_date = date.today()
        start_date = end_date.replace(day=1)  # First day of month

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        # Calculate spent so far in this category (including new receipt)
        category_receipts = [r for r in receipts if r.get('category') == category]
        spent_so_far = sum(r['amount'] for r in category_receipts) + amount

        # Get budget
        budget = profile.budget_categories.get(category, 0)

        # Calculate metrics
        percent_used = (spent_so_far / budget * 100) if budget > 0 else 0
        remaining = budget - spent_so_far
        days_left_in_month = (end_date.replace(day=28) + timedelta(days=4)).replace(day=1).day - end_date.day

        # Use LLM for intelligent alert
        prompt = f"""Analyze this spending situation and generate a helpful, personalized budget alert.

Current Situation:
- Category: {category}
- This purchase: ${amount:.2f} at {receipt.get('vendor', 'Unknown')}
- Month-to-date spent in {category}: ${spent_so_far:.2f}
- Monthly budget for {category}: ${budget:.2f}
- Budget used: {percent_used:.1f}%
- Remaining budget: ${remaining:.2f}
- Days left in month: {days_left_in_month}

Generate a helpful alert message that:
1. Informs the user of their current budget status
2. Provides context (are they on track, over budget, or approaching limit?)
3. Gives specific, actionable advice
4. Is encouraging but honest

Respond in JSON format:
{{
    "alert_level": "info/warning/critical",
    "message": "personalized alert message",
    "status": "on_track/approaching_limit/over_budget",
    "advice": "specific actionable advice",
    "should_notify": true/false
}}

Alert level guidelines:
- info: < 70% of budget used
- warning: 70-100% of budget used
- critical: > 100% of budget used

Return ONLY valid JSON."""

        system_message = "You are a helpful financial advisor who provides encouraging but honest budget alerts."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.4,
                max_tokens=500
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                # Fallback to rule-based
                return self._fallback_budget_alert(category, spent_so_far, budget, percent_used, remaining)

            return {
                "category": category,
                "receipt_amount": amount,
                "spent_so_far": round(spent_so_far, 2),
                "budget": budget,
                "percent_used": round(percent_used, 1),
                "remaining": round(remaining, 2),
                "days_left": days_left_in_month,
                "alert": result
            }

        except Exception as e:
            logger.error(f"Error in LLM budget alert: {e}")
            return self._fallback_budget_alert(category, spent_so_far, budget, percent_used, remaining)

    def generate_spending_insights_llm(self, user_id: str, receipts: List[Dict]) -> List[str]:
        """
        Generate intelligent spending insights using LLM analysis

        Args:
            user_id: User ID
            receipts: List of recent receipts

        Returns:
            List of insight strings
        """
        if not receipts:
            return ["No recent spending to analyze"]

        # Get user context
        profile = self.user_storage.ensure_profile_exists(user_id)
        goals = self.user_storage.get_all_goals(user_id)

        # Prepare spending summary
        category_breakdown = self._calculate_category_breakdown(receipts)
        total_spent = sum(r['amount'] for r in receipts)

        # Format for LLM
        category_summary = "\n".join([
            f"- {cat}: ${data['amount']:.2f} ({data['count']} transactions)"
            for cat, data in category_breakdown.items()
        ])

        active_goals_summary = "\n".join([
            f"- {g.name}: ${g.current_savings:.2f} / ${g.target_amount:.2f}"
            for g in goals if g.status == "on_track"
        ]) if goals else "None"

        prompt = f"""Analyze this user's spending and provide 3-5 intelligent, actionable insights.

User Profile:
- Monthly Income: ${profile.salary_monthly:.2f}

Recent Spending (this month):
- Total: ${total_spent:.2f}
{category_summary}

Active Goals:
{active_goals_summary}

Budget by Category:
{chr(10).join([f'- {cat}: ${amount:.2f}' for cat, amount in profile.budget_categories.items()])}

Provide insights that:
1. Identify concerning trends or positive patterns
2. Compare spending to budget and goals
3. Suggest specific actionable improvements
4. Are personalized and encouraging

Respond in JSON format:
{{
    "insights": [
        "insight 1",
        "insight 2",
        "insight 3"
    ]
}}

Keep each insight concise (1-2 sentences) and actionable.
Return ONLY valid JSON."""

        system_message = "You are a financial advisor who provides personalized, actionable spending insights."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.5,
                max_tokens=600
            )

            result = self.ollama.parse_json_response(response)

            if result and 'insights' in result:
                return result['insights']
            else:
                return self._generate_insights(category_breakdown, {}, 0, 0)

        except Exception as e:
            logger.error(f"Error generating LLM insights: {e}")
            return ["Unable to generate insights at this time"]

    def detect_spending_patterns_llm(self, user_id: str) -> Dict:
        """
        Use LLM to detect spending patterns and triggers

        Args:
            user_id: User ID

        Returns:
            Pattern analysis with triggers and recommendations
        """
        logger.info(f"PersonalFinanceAgent: Detecting spending patterns for {user_id}")

        # Get last 2 months of receipts
        end_date = date.today()
        start_date = end_date - relativedelta(months=2)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        if len(receipts) < 10:
            return {
                "patterns_found": 0,
                "message": "Not enough transaction history to detect patterns"
            }

        # Enrich receipts with temporal data
        enriched_receipts = []
        for r in receipts:
            try:
                dt = datetime.strptime(r['date'], "%Y-%m-%d")
                enriched_receipts.append({
                    **r,
                    "day_of_week": dt.strftime("%A"),
                    "is_weekend": dt.weekday() >= 5,
                    "time_of_month": "early" if dt.day <= 10 else "mid" if dt.day <= 20 else "late"
                })
            except:
                enriched_receipts.append(r)

        # Format for LLM
        receipt_summary = "\n".join([
            f"- {r['date']} ({r.get('day_of_week', 'N/A')}): {r['vendor']} - ${r['amount']:.2f} ({r['category']})"
            for r in enriched_receipts[:30]  # Last 30 transactions
        ])

        prompt = f"""Analyze these transactions to detect spending patterns and triggers.

Transactions (last 2 months):
{receipt_summary}

Identify:
1. Temporal patterns (specific days, weekends, time of month)
2. Category patterns (which categories dominate spending)
3. Spending triggers (events or situations that lead to spending)
4. Recurring expenses vs impulse purchases
5. Behavioral insights

Respond in JSON format:
{{
    "patterns": [
        {{
            "type": "temporal/category/behavioral",
            "description": "clear description",
            "frequency": "how often",
            "impact": "high/medium/low",
            "examples": ["specific examples"]
        }}
    ],
    "spending_triggers": [
        "trigger 1",
        "trigger 2"
    ],
    "recommendations": [
        "actionable recommendation 1",
        "actionable recommendation 2"
    ],
    "summary": "overall pattern summary"
}}

Return ONLY valid JSON."""

        system_message = "You are a behavioral finance expert who identifies spending patterns and provides actionable insights."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=1000
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                return {"patterns_found": 0, "message": "Could not analyze patterns"}

            return result

        except Exception as e:
            logger.error(f"Error in pattern detection: {e}")
            return {"patterns_found": 0, "error": str(e)}

    # ==================== HELPER METHODS ====================

    def _get_user_receipts(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Get user's receipts within date range"""
        all_chunks = self.vector_store.get_all_chunks()

        receipts = []
        seen_ids = set()

        for chunk in all_chunks:
            metadata = chunk.get('metadata', {})

            # Filter by user_id
            if metadata.get('user_id') != user_id:
                continue

            # Filter by date
            receipt_date_str = metadata.get('date')
            if not receipt_date_str:
                continue

            try:
                receipt_date = datetime.strptime(receipt_date_str, "%Y-%m-%d").date()
            except:
                continue

            if not (start_date <= receipt_date <= end_date):
                continue

            # Deduplicate by document_id
            doc_id = metadata.get('document_id')
            if doc_id in seen_ids:
                continue

            seen_ids.add(doc_id)

            receipts.append({
                'document_id': doc_id,
                'vendor': metadata.get('vendor', 'Unknown'),
                'date': receipt_date_str,
                'amount': metadata.get('amount', 0),
                'category': metadata.get('category', 'other'),
                'invoice_number': metadata.get('invoice_number')
            })

        return receipts

    def _calculate_category_breakdown(self, receipts: List[Dict]) -> Dict:
        """Calculate spending breakdown by category"""
        breakdown = {}

        for receipt in receipts:
            category = receipt['category']
            amount = receipt['amount']

            if category not in breakdown:
                breakdown[category] = {
                    'amount': 0.0,
                    'count': 0,
                    'avg_per_transaction': 0.0
                }

            breakdown[category]['amount'] += amount
            breakdown[category]['count'] += 1

        # Calculate averages
        for category, data in breakdown.items():
            data['amount'] = round(data['amount'], 2)
            data['avg_per_transaction'] = round(data['amount'] / data['count'], 2)

        return breakdown

    def _compare_to_budget(self, actual: Dict, budget: Dict) -> Dict:
        """Compare actual spending to budget"""
        comparison = {}

        for category, data in actual.items():
            budget_amount = budget.get(category, 0)
            actual_amount = data['amount']
            difference = budget_amount - actual_amount

            comparison[category] = {
                'budget': budget_amount,
                'actual': actual_amount,
                'difference': round(difference, 2),
                'status': 'under' if difference > 0 else 'over',
                'percent_of_budget': round((actual_amount / budget_amount * 100), 1) if budget_amount > 0 else 0
            }

        return comparison

    def _group_by_month(self, receipts: List[Dict]) -> Dict:
        """Group receipts by month"""
        monthly = {}

        for receipt in receipts:
            try:
                dt = datetime.strptime(receipt['date'], "%Y-%m-%d")
                month_key = dt.strftime("%Y-%m")

                if month_key not in monthly:
                    monthly[month_key] = {'total': 0.0, 'count': 0}

                monthly[month_key]['total'] += receipt['amount']
                monthly[month_key]['count'] += 1
            except:
                continue

        return monthly

    def _generate_insights(
        self,
        spending_by_category: Dict,
        vs_budget: Dict,
        percent_change: float,
        savings_rate: float
    ) -> List[str]:
        """Generate spending insights"""
        insights = []

        # Budget insights
        for category, comp in vs_budget.items():
            if comp['status'] == 'over':
                insights.append(
                    f"You spent ${comp['actual']:.2f} on {category} "
                    f"({abs(comp['percent_of_budget'] - 100):.0f}% over budget)"
                )
            elif comp['status'] == 'under' and comp['difference'] > 50:
                insights.append(f"Great job staying under budget on {category}!")

        # Trend insights
        if abs(percent_change) > 10:
            direction = "more" if percent_change > 0 else "less"
            insights.append(
                f"You spent {abs(percent_change):.1f}% {direction} this period compared to last period"
            )

        # Savings insights
        if savings_rate > 0.20:
            insights.append(f"Your savings rate ({savings_rate*100:.0f}%) is above average")
        elif savings_rate < 0.05:
            insights.append(f"Your savings rate ({savings_rate*100:.0f}%) is below recommended 10-20%")

        return insights

    def _fallback_budget_alert(
        self,
        category: str,
        spent_so_far: float,
        budget: float,
        percent_used: float,
        remaining: float
    ) -> Dict:
        """Fallback budget alert when LLM fails"""
        if percent_used >= 100:
            alert_level = "critical"
            status = "over_budget"
            message = f"You've exceeded your {category} budget by ${abs(remaining):.2f}"
            advice = f"Consider reducing {category} expenses for the rest of the month"
            should_notify = True
        elif percent_used >= 70:
            alert_level = "warning"
            status = "approaching_limit"
            message = f"You've used {percent_used:.0f}% of your {category} budget (${remaining:.2f} remaining)"
            advice = f"Be mindful of {category} spending for the rest of the month"
            should_notify = True
        else:
            alert_level = "info"
            status = "on_track"
            message = f"You're on track with {category} spending ({percent_used:.0f}% used)"
            advice = "Keep up the good work!"
            should_notify = False

        return {
            "category": category,
            "spent_so_far": round(spent_so_far, 2),
            "budget": budget,
            "percent_used": round(percent_used, 1),
            "remaining": round(remaining, 2),
            "alert": {
                "alert_level": alert_level,
                "message": message,
                "status": status,
                "advice": advice,
                "should_notify": should_notify
            }
        }


# Global agent instance
_personal_finance_agent = None


def get_personal_finance_agent() -> PersonalFinanceAgent:
    """Get global personal finance agent instance"""
    global _personal_finance_agent
    if _personal_finance_agent is None:
        _personal_finance_agent = PersonalFinanceAgent()
    return _personal_finance_agent
