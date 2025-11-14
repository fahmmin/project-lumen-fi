"""
Family Analytics Agent - Aggregated family financial analysis
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from backend.models.family import FamilyDashboard, FamilyMemberStats
from backend.utils.family_storage import family_storage
from backend.rag.retriever import search
from backend.utils.logger import logger


class FamilyAnalyticsAgent:
    """Analyzes aggregated family financial data"""

    def __init__(self):
        pass

    def get_family_dashboard(self, family_id: str, period: str = "month") -> Dict:
        """
        Generate aggregated family dashboard

        Args:
            family_id: Family ID
            period: 'month', 'quarter', or 'year'

        Returns:
            Complete family financial dashboard
        """
        try:
            # Get family
            family = family_storage.get_family_by_id(family_id)

            if not family:
                raise ValueError("Family not found")

            # Calculate date range
            end_date = datetime.now()
            if period == "month":
                start_date = end_date - relativedelta(months=1)
            elif period == "quarter":
                start_date = end_date - relativedelta(months=3)
            elif period == "year":
                start_date = end_date - relativedelta(years=1)
            else:
                start_date = end_date - relativedelta(months=1)

            # Aggregate data from all members
            member_spending = []
            total_family_spending = 0.0
            category_totals = {}

            for member in family.members:
                user_id = member.user_id

                # Get member's receipts
                receipts = self._get_user_receipts(user_id, start_date, end_date)

                # Calculate member totals
                member_total = sum(r.get('amount', 0) for r in receipts)
                total_family_spending += member_total

                # Aggregate by category
                member_categories = {}
                for receipt in receipts:
                    category = receipt.get('category', 'uncategorized')
                    amount = receipt.get('amount', 0)

                    member_categories[category] = member_categories.get(category, 0) + amount
                    category_totals[category] = category_totals.get(category, 0) + amount

                member_spending.append({
                    "user_id": user_id,
                    "display_name": member.display_name or f"User {user_id[:8]}",
                    "total_spent": round(member_total, 2),
                    "spending_by_category": {k: round(v, 2) for k, v in member_categories.items()},
                    "percentage": 0  # Will calculate after
                })

            # Calculate percentages
            for member_data in member_spending:
                if total_family_spending > 0:
                    member_data["percentage"] = round((member_data["total_spent"] / total_family_spending) * 100, 1)

            # Sort by spending
            member_spending.sort(key=lambda x: x["total_spent"], reverse=True)

            # Get top spenders
            top_spenders = member_spending[:3]

            # Calculate shared budget status
            shared_budget_status = None
            if family.shared_budget:
                shared_budget_status = {}
                for category, budget_limit in family.shared_budget.items():
                    actual_spent = category_totals.get(category, 0)
                    percentage = (actual_spent / budget_limit * 100) if budget_limit > 0 else 0

                    shared_budget_status[category] = {
                        "budget": budget_limit,
                        "spent": round(actual_spent, 2),
                        "remaining": round(budget_limit - actual_spent, 2),
                        "percentage": round(percentage, 1),
                        "status": "over_budget" if actual_spent > budget_limit else "within_budget"
                    }

            # Generate insights
            insights = self._generate_family_insights(
                member_spending,
                category_totals,
                shared_budget_status,
                period
            )

            # Calculate average per member
            avg_per_member = total_family_spending / len(family.members) if family.members else 0

            dashboard = FamilyDashboard(
                family_id=family_id,
                family_name=family.name,
                period=period,
                member_count=len(family.members),
                summary={
                    "total_family_spending": round(total_family_spending, 2),
                    "average_per_member": round(avg_per_member, 2),
                    "period": period,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                spending_by_member=member_spending,
                spending_by_category={k: round(v, 2) for k, v in category_totals.items()},
                shared_budget_status=shared_budget_status,
                top_spenders=top_spenders,
                insights=insights
            )

            return dashboard.model_dump()

        except Exception as e:
            logger.error(f"Error generating family dashboard: {str(e)}")
            raise

    def get_member_comparison(self, family_id: str, user_id: str, period: str = "month") -> Dict:
        """
        Compare a member's spending to family averages

        Args:
            family_id: Family ID
            user_id: User to compare
            period: Time period

        Returns:
            Comparison stats
        """
        try:
            # Get family dashboard
            dashboard = self.get_family_dashboard(family_id, period)

            # Find user's data
            user_data = None
            for member in dashboard["spending_by_member"]:
                if member["user_id"] == user_id:
                    user_data = member
                    break

            if not user_data:
                raise ValueError("User not found in family")

            # Calculate comparisons
            avg_spending = dashboard["summary"]["average_per_member"]
            user_spending = user_data["total_spent"]

            difference = user_spending - avg_spending
            percentage_diff = (difference / avg_spending * 100) if avg_spending > 0 else 0

            # Category comparisons
            category_comparisons = {}
            for category, family_total in dashboard["spending_by_category"].items():
                avg_category = family_total / dashboard["member_count"]
                user_category = user_data["spending_by_category"].get(category, 0)

                diff = user_category - avg_category
                diff_pct = (diff / avg_category * 100) if avg_category > 0 else 0

                category_comparisons[category] = {
                    "user_spent": round(user_category, 2),
                    "family_average": round(avg_category, 2),
                    "difference": round(diff, 2),
                    "percentage_difference": round(diff_pct, 1),
                    "status": "above_average" if diff > 0 else "below_average"
                }

            return {
                "user_id": user_id,
                "display_name": user_data["display_name"],
                "period": period,
                "overall": {
                    "user_spending": round(user_spending, 2),
                    "family_average": round(avg_spending, 2),
                    "difference": round(difference, 2),
                    "percentage_difference": round(percentage_diff, 1),
                    "status": "above_average" if difference > 0 else "below_average",
                    "rank": dashboard["spending_by_member"].index(user_data) + 1,
                    "total_members": dashboard["member_count"]
                },
                "by_category": category_comparisons,
                "insights": self._generate_member_insights(user_data, dashboard)
            }

        except Exception as e:
            logger.error(f"Error generating member comparison: {str(e)}")
            raise

    def _get_user_receipts(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get user's receipts in date range"""
        # Search for user's receipts
        query = f"user:{user_id}"
        results = search(query, top_k=1000, use_hyde=False)

        receipts = []
        for result in results:
            metadata = result.get('metadata', {})

            # Filter by user_id
            if metadata.get('user_id') != user_id:
                continue

            # Check date range
            receipt_date_str = metadata.get('date')
            if receipt_date_str:
                try:
                    receipt_date = datetime.fromisoformat(receipt_date_str)
                    if start_date <= receipt_date <= end_date:
                        receipts.append(metadata)
                except:
                    pass

        return receipts

    def _generate_family_insights(
        self,
        member_spending: List[Dict],
        category_totals: Dict,
        budget_status: Optional[Dict],
        period: str
    ) -> List[str]:
        """Generate insights for family"""
        insights = []

        # Top spender insight
        if member_spending:
            top_spender = member_spending[0]
            insights.append(
                f"{top_spender['display_name']} is the highest spender at ${top_spender['total_spent']:.2f} ({top_spender['percentage']:.0f}% of family total)"
            )

        # Top category
        if category_totals:
            top_category = max(category_totals.items(), key=lambda x: x[1])
            insights.append(
                f"Family's biggest expense category is {top_category[0]} at ${top_category[1]:.2f}"
            )

        # Budget insights
        if budget_status:
            over_budget = [cat for cat, status in budget_status.items() if status["status"] == "over_budget"]
            if over_budget:
                insights.append(
                    f"⚠️ Family is over budget in {len(over_budget)} categories: {', '.join(over_budget)}"
                )
            else:
                insights.append("✅ Family is within budget in all categories!")

        # Spending distribution
        if len(member_spending) > 1:
            std_dev = self._calculate_std_dev([m["total_spent"] for m in member_spending])
            avg = sum(m["total_spent"] for m in member_spending) / len(member_spending)

            if std_dev / avg > 0.5:  # High variance
                insights.append("Spending varies significantly between family members")
            else:
                insights.append("Family spending is fairly balanced across members")

        return insights

    def _generate_member_insights(self, user_data: Dict, dashboard: Dict) -> List[str]:
        """Generate insights for specific member"""
        insights = []

        # Overall comparison
        avg = dashboard["summary"]["average_per_member"]
        user_total = user_data["total_spent"]

        if user_total > avg * 1.2:
            insights.append(f"You're spending 20%+ more than the family average")
        elif user_total < avg * 0.8:
            insights.append(f"You're spending 20%+ less than the family average")
        else:
            insights.append("Your spending is close to the family average")

        # Category-specific
        user_categories = user_data["spending_by_category"]
        if user_categories:
            top_category = max(user_categories.items(), key=lambda x: x[1])
            insights.append(f"Your biggest expense is {top_category[0]} at ${top_category[1]:.2f}")

        return insights

    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values:
            return 0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5


# Global instance
family_analytics_agent = FamilyAnalyticsAgent()
