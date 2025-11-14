"""
PROJECT LUMEN - Behavioral Spending Agent
Analyzes spending psychology and behavioral patterns
"""

from typing import Dict, List
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import numpy as np

from backend.rag.vector_store import get_vector_store
from backend.utils.logger import logger


class BehavioralAgent:
    """Analyzes spending behavior and psychology"""

    def __init__(self):
        self.vector_store = get_vector_store()

    def analyze_behavior(self, user_id: str) -> Dict:
        """
        Analyze spending psychology

        Args:
            user_id: User ID

        Returns:
            Behavioral analysis
        """
        logger.info(f"BehavioralAgent: Analyzing behavior for {user_id}")

        # Get last 3 months
        end_date = date.today()
        start_date = end_date - relativedelta(months=3)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        if len(receipts) < 10:
            return {
                "user_id": user_id,
                "analysis_period": "last_3_months",
                "impulse_score": 0.0,
                "patterns": [],
                "recommendations": ["Not enough data for behavioral analysis"],
                "data_points": len(receipts)
            }

        patterns = []

        # Day of week analysis
        dow_pattern = self._analyze_day_of_week(receipts)
        if dow_pattern:
            patterns.append(dow_pattern)

        # Time of day analysis (if timestamp available)
        tod_pattern = self._analyze_time_of_day(receipts)
        if tod_pattern:
            patterns.append(tod_pattern)

        # Impulse purchase detection
        impulse_pattern = self._detect_impulse_purchases(receipts)
        if impulse_pattern:
            patterns.append(impulse_pattern)

        # Calculate overall impulse score
        impulse_score = self._calculate_impulse_score(receipts)

        # Generate recommendations
        recommendations = self._generate_recommendations(patterns, impulse_score)

        return {
            "user_id": user_id,
            "analysis_period": "last_3_months",
            "impulse_score": round(impulse_score, 2),
            "patterns": patterns,
            "recommendations": recommendations,
            "data_points": len(receipts)
        }

    # ==================== HELPER METHODS ====================

    def _get_user_receipts(self, user_id: str, start_date: date, end_date: date) -> List[Dict]:
        """Get user's receipts"""
        all_chunks = self.vector_store.get_all_chunks()

        receipts = []
        seen_ids = set()

        for chunk in all_chunks:
            metadata = chunk.get('metadata', {})

            if metadata.get('user_id') != user_id:
                continue

            receipt_date_str = metadata.get('date')
            if not receipt_date_str:
                continue

            try:
                receipt_datetime = datetime.strptime(receipt_date_str, "%Y-%m-%d")
                receipt_date = receipt_datetime.date()
            except:
                continue

            if not (start_date <= receipt_date <= end_date):
                continue

            doc_id = metadata.get('document_id')
            if doc_id in seen_ids:
                continue

            seen_ids.add(doc_id)

            receipts.append({
                'document_id': doc_id,
                'vendor': metadata.get('vendor', 'Unknown'),
                'date': receipt_date,
                'datetime': receipt_datetime,
                'amount': metadata.get('amount', 0),
                'category': metadata.get('category', 'other')
            })

        return receipts

    def _analyze_day_of_week(self, receipts: List[Dict]) -> Dict:
        """Analyze spending by day of week"""
        weekday_spending = defaultdict(list)

        for receipt in receipts:
            day_name = receipt['date'].strftime("%A")
            weekday_spending[day_name].append(receipt['amount'])

        # Calculate averages
        weekday_avg = {}
        for day, amounts in weekday_spending.items():
            weekday_avg[day] = sum(amounts) / len(amounts)

        if not weekday_avg:
            return None

        # Check for weekend vs weekday pattern
        weekend_days = ['Saturday', 'Sunday']
        weekday_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        weekend_avg = np.mean([v for k, v in weekday_avg.items() if k in weekend_days])
        weekday_avg_val = np.mean([v for k, v in weekday_avg.items() if k in weekday_days])

        if weekend_avg > weekday_avg_val * 1.5:
            ratio = weekend_avg / weekday_avg_val if weekday_avg_val > 0 else 0
            return {
                "type": "day_of_week",
                "finding": f"You spend {ratio:.1f}x more on weekends than weekdays",
                "data": {
                    "weekday_avg": round(weekday_avg_val, 2),
                    "weekend_avg": round(weekend_avg, 2),
                    "ratio": round(ratio, 1)
                },
                "severity": "medium" if ratio > 2 else "low"
            }

        return None

    def _analyze_time_of_day(self, receipts: List[Dict]) -> Dict:
        """Analyze spending by time of day"""
        # Group by time of day (if datetime has time info)
        late_night = []  # 11pm - 1am
        daytime = []

        for receipt in receipts:
            hour = receipt['datetime'].hour if hasattr(receipt['datetime'], 'hour') else 12

            if 23 <= hour or hour <= 1:  # 11pm - 1am
                late_night.append(receipt)
            else:
                daytime.append(receipt)

        if len(late_night) >= 5:  # Significant late-night purchases
            late_night_total = sum(r['amount'] for r in late_night)

            return {
                "type": "time_of_day",
                "finding": f"Higher spending detected between 11pm-1am (impulse purchases)",
                "data": {
                    "late_night_transactions": len(late_night),
                    "late_night_total": round(late_night_total, 2)
                },
                "severity": "medium"
            }

        return None

    def _detect_impulse_purchases(self, receipts: List[Dict]) -> Dict:
        """Detect impulse purchase patterns"""
        # Group receipts by date
        daily_receipts = defaultdict(list)

        for receipt in receipts:
            daily_receipts[receipt['date']].append(receipt)

        # Find days with multiple purchases
        multi_purchase_days = {
            day: receipts_list
            for day, receipts_list in daily_receipts.items()
            if len(receipts_list) >= 3
        }

        if multi_purchase_days:
            total_days = len(multi_purchase_days)
            total_amount = sum(
                sum(r['amount'] for r in receipts_list)
                for receipts_list in multi_purchase_days.values()
            )

            return {
                "type": "impulse_purchases",
                "finding": f"Multiple purchases on same day detected ({total_days} days)",
                "data": {
                    "multi_purchase_days": total_days,
                    "total_impulse_amount": round(total_amount, 2)
                },
                "severity": "medium" if total_days > 5 else "low"
            }

        return None

    def _calculate_impulse_score(self, receipts: List[Dict]) -> float:
        """
        Calculate impulse spending score (0-1)

        Factors:
        - Multiple purchases per day
        - Small frequent purchases
        - Weekend overspending
        """
        if not receipts:
            return 0.0

        score = 0.0

        # Factor 1: Multiple purchases per day
        daily_counts = defaultdict(int)
        for receipt in receipts:
            daily_counts[receipt['date']] += 1

        avg_purchases_per_day = np.mean(list(daily_counts.values()))
        if avg_purchases_per_day > 2:
            score += 0.3

        # Factor 2: Small frequent purchases (< $20)
        small_purchases = [r for r in receipts if r['amount'] < 20]
        if len(small_purchases) / len(receipts) > 0.4:  # >40% are small
            score += 0.25

        # Factor 3: Weekend overspending
        weekend_receipts = [r for r in receipts if r['date'].weekday() in [5, 6]]
        if len(weekend_receipts) / len(receipts) > 0.35:  # >35% on weekends
            score += 0.25

        # Factor 4: Category diversity (many categories = impulse)
        categories = set(r['category'] for r in receipts)
        if len(categories) > 5:
            score += 0.2

        return min(score, 1.0)

    def _generate_recommendations(self, patterns: List[Dict], impulse_score: float) -> List[str]:
        """Generate behavioral recommendations"""
        recommendations = []

        for pattern in patterns:
            if pattern['type'] == 'day_of_week':
                recommendations.append("Set a weekend spending limit")
                recommendations.append("Plan weekend activities that don't involve shopping")

            elif pattern['type'] == 'time_of_day':
                recommendations.append("Avoid online shopping late at night")
                recommendations.append("Use browser extensions to block shopping sites after 10pm")

            elif pattern['type'] == 'impulse_purchases':
                recommendations.append("Use the 24-hour rule for purchases over $50")
                recommendations.append("Unsubscribe from promotional emails")

        if impulse_score > 0.5:
            recommendations.append("Consider using a 'cooling off' period before making purchases")
            recommendations.append("Remove saved payment methods from shopping sites")

        if not recommendations:
            recommendations.append("Your spending patterns appear healthy!")

        return recommendations


# Global agent instance
_behavioral_agent = None


def get_behavioral_agent() -> BehavioralAgent:
    """Get global behavioral agent instance"""
    global _behavioral_agent
    if _behavioral_agent is None:
        _behavioral_agent = BehavioralAgent()
    return _behavioral_agent
