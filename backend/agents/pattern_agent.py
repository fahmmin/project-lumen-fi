"""
PROJECT LUMEN - Pattern Detection Agent
Detects recurring expenses and generates smart reminders
"""

from typing import Dict, List
from datetime import date, datetime, timedelta
from collections import defaultdict
from dateutil.relativedelta import relativedelta
import uuid

from backend.rag.vector_store import get_vector_store
from backend.models.reminder import RecurringPattern, Reminder, ReminderType, PatternFrequency
from backend.utils.logger import logger


class PatternAgent:
    """Detects spending patterns and generates reminders"""

    def __init__(self):
        self.vector_store = get_vector_store()

    def detect_patterns(self, user_id: str) -> List[RecurringPattern]:
        """
        Detect recurring spending patterns

        Args:
            user_id: User ID

        Returns:
            List of detected patterns
        """
        logger.info(f"PatternAgent: Detecting patterns for {user_id}")

        # Get last 12 months of receipts
        end_date = date.today()
        start_date = end_date - relativedelta(months=12)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        if len(receipts) < 5:
            return []

        # Group by vendor
        vendor_groups = defaultdict(list)
        for receipt in receipts:
            vendor = receipt['vendor']
            vendor_groups[vendor].append(receipt)

        patterns = []

        # Analyze each vendor group
        for vendor, vendor_receipts in vendor_groups.items():
            if len(vendor_receipts) < 3:
                continue

            # Check for monthly pattern
            monthly_pattern = self._detect_monthly_pattern(vendor_receipts)
            if monthly_pattern:
                pattern_id = f"pat_{uuid.uuid4().hex[:12]}"
                patterns.append(RecurringPattern(
                    pattern_id=pattern_id,
                    user_id=user_id,
                    **monthly_pattern
                ))

            # Check for weekly pattern
            weekly_pattern = self._detect_weekly_pattern(vendor_receipts)
            if weekly_pattern:
                pattern_id = f"pat_{uuid.uuid4().hex[:12]}"
                patterns.append(RecurringPattern(
                    pattern_id=pattern_id,
                    user_id=user_id,
                    **weekly_pattern
                ))

        logger.info(f"PatternAgent: Detected {len(patterns)} patterns")
        return patterns

    def generate_reminders(self, user_id: str) -> List[Reminder]:
        """
        Generate smart reminders based on patterns

        Args:
            user_id: User ID

        Returns:
            List of active reminders
        """
        patterns = self.detect_patterns(user_id)
        reminders = []

        today = date.today()

        for pattern in patterns:
            # Check if next expected date is soon
            days_until = (pattern.next_expected - today).days

            if 0 <= days_until <= 7:
                # Generate reminder
                reminder = self._create_reminder_from_pattern(pattern)
                reminders.append(reminder)

        logger.info(f"PatternAgent: Generated {len(reminders)} reminders")
        return reminders

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
                receipt_date = datetime.strptime(receipt_date_str, "%Y-%m-%d").date()
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
                'amount': metadata.get('amount', 0),
                'category': metadata.get('category', 'other')
            })

        return receipts

    def _detect_monthly_pattern(self, receipts: List[Dict]) -> Dict:
        """Detect monthly recurring pattern"""
        if len(receipts) < 3:
            return None

        # Sort by date
        sorted_receipts = sorted(receipts, key=lambda x: x['date'])

        # Check if purchases are roughly monthly
        intervals = []
        for i in range(1, len(sorted_receipts)):
            days = (sorted_receipts[i]['date'] - sorted_receipts[i-1]['date']).days
            intervals.append(days)

        avg_interval = sum(intervals) / len(intervals) if intervals else 0

        # Monthly = 25-35 days
        if 25 <= avg_interval <= 35:
            # Extract typical day of month
            days_of_month = [r['date'].day for r in sorted_receipts]
            typical_day = int(sum(days_of_month) / len(days_of_month))

            # Calculate typical amount
            amounts = [r['amount'] for r in sorted_receipts]
            typical_amount = sum(amounts) / len(amounts)

            # Calculate next expected date
            last_date = sorted_receipts[-1]['date']
            next_expected = last_date + relativedelta(months=1)

            # Adjust to typical day
            try:
                next_expected = next_expected.replace(day=typical_day)
            except ValueError:
                pass  # Keep as is if day doesn't exist in month

            confidence = 0.7 + (len(receipts) * 0.05)  # Higher confidence with more data
            confidence = min(confidence, 0.95)

            return {
                'pattern_type': f"monthly_{sorted_receipts[0]['category']}",
                'vendor': sorted_receipts[0]['vendor'],
                'category': sorted_receipts[0]['category'],
                'frequency': PatternFrequency.MONTHLY,
                'typical_day': typical_day,
                'typical_amount': typical_amount,
                'last_purchase': sorted_receipts[-1]['date'],
                'next_expected': next_expected,
                'occurrences': len(receipts),
                'confidence': confidence
            }

        return None

    def _detect_weekly_pattern(self, receipts: List[Dict]) -> Dict:
        """Detect weekly recurring pattern"""
        if len(receipts) < 4:
            return None

        sorted_receipts = sorted(receipts, key=lambda x: x['date'])

        # Check intervals
        intervals = []
        for i in range(1, len(sorted_receipts)):
            days = (sorted_receipts[i]['date'] - sorted_receipts[i-1]['date']).days
            intervals.append(days)

        avg_interval = sum(intervals) / len(intervals) if intervals else 0

        # Weekly = 5-9 days
        if 5 <= avg_interval <= 9:
            # Get day of week
            days_of_week = [r['date'].strftime("%A") for r in sorted_receipts]
            most_common_day = max(set(days_of_week), key=days_of_week.count)

            amounts = [r['amount'] for r in sorted_receipts]
            typical_amount = sum(amounts) / len(amounts)

            last_date = sorted_receipts[-1]['date']
            days_ahead = (7 - (last_date.weekday() - sorted_receipts[0]['date'].weekday())) % 7
            next_expected = last_date + timedelta(days=days_ahead if days_ahead > 0 else 7)

            confidence = 0.6 + (len(receipts) * 0.05)
            confidence = min(confidence, 0.90)

            return {
                'pattern_type': f"weekly_{sorted_receipts[0]['category']}",
                'vendor': sorted_receipts[0]['vendor'],
                'category': sorted_receipts[0]['category'],
                'frequency': PatternFrequency.WEEKLY,
                'typical_day_of_week': most_common_day,
                'typical_amount': typical_amount,
                'last_purchase': sorted_receipts[-1]['date'],
                'next_expected': next_expected,
                'occurrences': len(receipts),
                'confidence': confidence
            }

        return None

    def _create_reminder_from_pattern(self, pattern: RecurringPattern) -> Reminder:
        """Create a reminder from a pattern"""
        if pattern.frequency == PatternFrequency.MONTHLY:
            message = (
                f"You usually buy {pattern.category} from {pattern.vendor} "
                f"around the {pattern.typical_day}{'st' if pattern.typical_day == 1 else 'th'} — time to restock!"
            )
        elif pattern.frequency == PatternFrequency.WEEKLY:
            message = (
                f"It's {pattern.typical_day_of_week} — you usually visit {pattern.vendor} "
                f"for {pattern.category} (typically ${pattern.typical_amount:.2f})"
            )
        else:
            message = f"Reminder: {pattern.vendor} - {pattern.category}"

        reminder_id = f"rem_{uuid.uuid4().hex[:12]}"

        return Reminder(
            reminder_id=reminder_id,
            user_id=pattern.user_id,
            reminder_type=ReminderType.RECURRING_EXPENSE,
            message=message,
            category=pattern.category,
            typical_amount=pattern.typical_amount,
            typical_vendor=pattern.vendor,
            next_expected_date=pattern.next_expected,
            confidence=pattern.confidence
        )


# Global agent instance
_pattern_agent = None


def get_pattern_agent() -> PatternAgent:
    """Get global pattern agent instance"""
    global _pattern_agent
    if _pattern_agent is None:
        _pattern_agent = PatternAgent()
    return _pattern_agent
