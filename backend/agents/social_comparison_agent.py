"""
Social Comparison Agent - Anonymous spending comparisons
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import json

from backend.rag.retriever import search
from backend.utils.logger import logger


class SocialComparisonAgent:
    """Provides anonymous spending comparisons across users"""

    def __init__(self):
        self.stats_dir = "backend/data/social_stats"
        os.makedirs(self.stats_dir, exist_ok=True)

    def get_user_percentile(self, user_id: str, period: str = "month") -> Dict:
        """
        Get user's spending percentile compared to all users

        Args:
            user_id: User ID
            period: 'month', 'quarter', or 'year'

        Returns:
            Percentile rankings and comparisons
        """
        try:
            # Get all user spending data
            all_user_data = self._get_all_user_spending(period)

            if not all_user_data:
                return {
                    "error": "Not enough data for comparison",
                    "user_id": user_id,
                    "period": period
                }

            # Find user's data
            user_data = None
            for data in all_user_data:
                if data["user_id"] == user_id:
                    user_data = data
                    break

            if not user_data:
                return {
                    "error": "User not found",
                    "user_id": user_id,
                    "period": period
                }

            # Calculate percentiles
            total_spending_list = [d["total_spent"] for d in all_user_data]
            total_spending_list.sort()

            user_total = user_data["total_spent"]
            user_rank = sum(1 for x in total_spending_list if x < user_total)
            percentile = (user_rank / len(total_spending_list)) * 100 if total_spending_list else 0

            # Calculate category percentiles
            category_percentiles = {}
            for category, amount in user_data["by_category"].items():
                category_amounts = [
                    d["by_category"].get(category, 0)
                    for d in all_user_data
                    if category in d["by_category"]
                ]

                if category_amounts:
                    category_amounts.sort()
                    cat_rank = sum(1 for x in category_amounts if x < amount)
                    cat_percentile = (cat_rank / len(category_amounts)) * 100

                    # Calculate average
                    avg_amount = sum(category_amounts) / len(category_amounts)

                    category_percentiles[category] = {
                        "user_spent": round(amount, 2),
                        "percentile": round(cat_percentile, 1),
                        "average": round(avg_amount, 2),
                        "above_average": amount > avg_amount,
                        "difference": round(amount - avg_amount, 2)
                    }

            # Generate insights
            insights = self._generate_comparison_insights(
                percentile,
                user_total,
                sum(total_spending_list) / len(total_spending_list),
                category_percentiles
            )

            return {
                "user_id": user_id,
                "period": period,
                "overall": {
                    "total_spent": round(user_total, 2),
                    "percentile": round(percentile, 1),
                    "rank": user_rank + 1,
                    "total_users": len(all_user_data),
                    "average_spending": round(sum(total_spending_list) / len(total_spending_list), 2),
                    "status": self._get_spending_status(percentile)
                },
                "by_category": category_percentiles,
                "insights": insights
            }

        except Exception as e:
            logger.error(f"Error getting user percentile: {str(e)}")
            raise

    def get_category_leaderboard(self, category: str, period: str = "month", limit: int = 10) -> Dict:
        """
        Get top spenders in a category (anonymized)

        Args:
            category: Category name
            period: Time period
            limit: Number of top users

        Returns:
            Anonymized leaderboard
        """
        try:
            all_user_data = self._get_all_user_spending(period)

            # Filter and sort by category
            category_data = []
            for data in all_user_data:
                cat_amount = data["by_category"].get(category, 0)
                if cat_amount > 0:
                    category_data.append({
                        "user_id": data["user_id"],
                        "amount": cat_amount
                    })

            category_data.sort(key=lambda x: x["amount"], reverse=True)

            # Create anonymized leaderboard
            leaderboard = []
            for rank, entry in enumerate(category_data[:limit], start=1):
                leaderboard.append({
                    "rank": rank,
                    "display_name": f"User_{entry['user_id'][:4]}",
                    "amount": round(entry["amount"], 2)
                })

            # Calculate stats
            amounts = [e["amount"] for e in category_data]
            avg = sum(amounts) / len(amounts) if amounts else 0

            return {
                "category": category,
                "period": period,
                "leaderboard": leaderboard,
                "stats": {
                    "total_users": len(category_data),
                    "average_spending": round(avg, 2),
                    "highest": round(max(amounts), 2) if amounts else 0,
                    "lowest": round(min(amounts), 2) if amounts else 0
                }
            }

        except Exception as e:
            logger.error(f"Error getting category leaderboard: {str(e)}")
            raise

    def _get_all_user_spending(self, period: str) -> List[Dict]:
        """
        Get spending data for all users

        Returns:
            List of {user_id, total_spent, by_category}
        """
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

        # Get all receipts
        all_receipts = search("receipt", top_k=10000, use_hyde=False)

        # Group by user
        user_spending = {}

        for result in all_receipts:
            metadata = result.get('metadata', {})
            user_id = metadata.get('user_id')

            if not user_id:
                continue

            # Check date range
            receipt_date_str = metadata.get('date')
            if receipt_date_str:
                try:
                    receipt_date = datetime.fromisoformat(receipt_date_str)
                    if not (start_date <= receipt_date <= end_date):
                        continue
                except:
                    continue

            amount = metadata.get('amount', 0)
            category = metadata.get('category', 'uncategorized')

            if user_id not in user_spending:
                user_spending[user_id] = {
                    "user_id": user_id,
                    "total_spent": 0,
                    "by_category": {}
                }

            user_spending[user_id]["total_spent"] += amount
            user_spending[user_id]["by_category"][category] = \
                user_spending[user_id]["by_category"].get(category, 0) + amount

        return list(user_spending.values())

    def _get_spending_status(self, percentile: float) -> str:
        """Get spending status description"""
        if percentile >= 90:
            return "top_10_percent"
        elif percentile >= 75:
            return "above_average"
        elif percentile >= 50:
            return "average"
        elif percentile >= 25:
            return "below_average"
        else:
            return "bottom_25_percent"

    def _generate_comparison_insights(
        self,
        percentile: float,
        user_total: float,
        avg_total: float,
        category_percentiles: Dict
    ) -> List[str]:
        """Generate comparison insights"""
        insights = []

        # Overall insight
        if percentile >= 75:
            diff = user_total - avg_total
            insights.append(f"You're spending more than 75% of users (${diff:.2f} above average)")
        elif percentile <= 25:
            diff = avg_total - user_total
            insights.append(f"You're spending less than 75% of users (${diff:.2f} below average)")
        else:
            insights.append("Your spending is close to the average user")

        # Category insights
        high_categories = [
            cat for cat, data in category_percentiles.items()
            if data["percentile"] >= 75
        ]

        if high_categories:
            insights.append(f"You're a high spender in: {', '.join(high_categories)}")

        low_categories = [
            cat for cat, data in category_percentiles.items()
            if data["percentile"] <= 25
        ]

        if low_categories:
            insights.append(f"You're saving well in: {', '.join(low_categories)}")

        return insights


# Global instance
social_comparison_agent = SocialComparisonAgent()
