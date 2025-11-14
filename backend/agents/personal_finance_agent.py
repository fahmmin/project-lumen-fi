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
from backend.utils.logger import logger


class PersonalFinanceAgent:
    """Analyzes personal finance and provides insights"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.user_storage = get_user_storage()
        self.forecaster = TimeSeriesForecaster()

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


# Global agent instance
_personal_finance_agent = None


def get_personal_finance_agent() -> PersonalFinanceAgent:
    """Get global personal finance agent instance"""
    global _personal_finance_agent
    if _personal_finance_agent is None:
        _personal_finance_agent = PersonalFinanceAgent()
    return _personal_finance_agent
