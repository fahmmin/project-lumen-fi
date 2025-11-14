"""
PROJECT LUMEN - Subscription Detector Agent
Detects and tracks subscription services
"""

from typing import Dict, List
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import uuid

from backend.rag.vector_store import get_vector_store
from backend.models.subscription import Subscription, SubscriptionStatus, UsageEstimate
from backend.utils.logger import logger


class SubscriptionAgent:
    """Detects and analyzes subscription services"""

    # Common subscription keywords
    SUBSCRIPTION_KEYWORDS = [
        'netflix', 'spotify', 'amazon prime', 'hulu', 'disney', 'apple music',
        'youtube', 'gym', 'fitness', 'membership', 'subscription', 'monthly',
        'adobe', 'microsoft', 'office 365', 'dropbox', 'icloud'
    ]

    def __init__(self):
        self.vector_store = get_vector_store()

    def detect_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        Detect subscription services

        Args:
            user_id: User ID

        Returns:
            List of detected subscriptions
        """
        logger.info(f"SubscriptionAgent: Detecting subscriptions for {user_id}")

        # Get last 12 months
        end_date = date.today()
        start_date = end_date - relativedelta(months=12)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        # Group by vendor
        vendor_groups = defaultdict(list)
        for receipt in receipts:
            vendor = receipt['vendor'].lower()
            # Check if vendor matches subscription keywords
            if any(keyword in vendor for keyword in self.SUBSCRIPTION_KEYWORDS):
                vendor_groups[receipt['vendor']].append(receipt)

        # Also detect by recurring amounts
        amount_groups = defaultdict(list)
        for receipt in receipts:
            # Round to nearest dollar to group similar amounts
            amount_key = round(receipt['amount'])
            amount_groups[amount_key].append(receipt)

        # Merge groups
        for amount, group in amount_groups.items():
            if len(group) >= 3:  # Recurring at least 3 times
                vendor = group[0]['vendor']
                if vendor not in vendor_groups:
                    # Check if truly recurring (monthly)
                    if self._is_recurring(group):
                        vendor_groups[vendor] = group

        subscriptions = []

        for vendor, vendor_receipts in vendor_groups.items():
            if len(vendor_receipts) < 2:
                continue

            subscription = self._create_subscription(user_id, vendor, vendor_receipts)
            if subscription:
                subscriptions.append(subscription)

        logger.info(f"SubscriptionAgent: Detected {len(subscriptions)} subscriptions")
        return subscriptions

    def find_unused_subscriptions(self, user_id: str) -> List[Dict]:
        """
        Find unused subscriptions

        Args:
            user_id: User ID

        Returns:
            List of unused subscriptions with savings info
        """
        subscriptions = self.detect_subscriptions(user_id)
        unused = []

        today = date.today()

        for subscription in subscriptions:
            if subscription.status == SubscriptionStatus.UNUSED:
                # Calculate potential savings
                months_unused = (today.year - subscription.last_charge.year) * 12 + \
                               (today.month - subscription.last_charge.month)

                monthly_cost = subscription.amount
                annual_savings = monthly_cost * 12

                unused.append({
                    "subscription_id": subscription.subscription_id,
                    "name": subscription.name,
                    "amount": subscription.amount,
                    "months_unused": months_unused,
                    "potential_savings_annual": round(annual_savings, 2),
                    "last_charge": subscription.last_charge.isoformat(),
                    "recommendation": f"Cancel - no usage detected in {months_unused} months"
                })

        return unused

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

    def _is_recurring(self, receipts: List[Dict]) -> bool:
        """Check if receipts represent recurring charges"""
        if len(receipts) < 3:
            return False

        sorted_receipts = sorted(receipts, key=lambda x: x['date'])

        # Check intervals
        intervals = []
        for i in range(1, len(sorted_receipts)):
            days = (sorted_receipts[i]['date'] - sorted_receipts[i-1]['date']).days
            intervals.append(days)

        avg_interval = sum(intervals) / len(intervals)

        # Monthly = 25-35 days
        return 25 <= avg_interval <= 35

    def _create_subscription(self, user_id: str, vendor: str, receipts: List[Dict]) -> Subscription:
        """Create subscription object from receipts"""
        sorted_receipts = sorted(receipts, key=lambda x: x['date'])

        # Calculate average amount (should be consistent for subscriptions)
        amounts = [r['amount'] for r in sorted_receipts]
        avg_amount = sum(amounts) / len(amounts)

        # Check amount consistency
        amount_variance = max(amounts) - min(amounts)
        if amount_variance > avg_amount * 0.1:  # More than 10% variance
            return None  # Probably not a subscription

        first_receipt = sorted_receipts[0]
        last_receipt = sorted_receipts[-1]

        # Billing day (most common day of month)
        billing_days = [r['date'].day for r in sorted_receipts]
        billing_day = max(set(billing_days), key=billing_days.count)

        total_spent = sum(amounts)

        # Determine status (unused if last charge was more than 2 months ago)
        today = date.today()
        months_since_last = (today.year - last_receipt['date'].year) * 12 + \
                           (today.month - last_receipt['date'].month)

        if months_since_last > 2:
            status = SubscriptionStatus.UNUSED
            usage = UsageEstimate.NONE
        else:
            status = SubscriptionStatus.ACTIVE
            # Simple heuristic: if charged every month, high usage
            if len(receipts) >= 10:
                usage = UsageEstimate.HIGH
            elif len(receipts) >= 5:
                usage = UsageEstimate.MEDIUM
            else:
                usage = UsageEstimate.LOW

        subscription_id = f"sub_{uuid.uuid4().hex[:12]}"

        return Subscription(
            subscription_id=subscription_id,
            user_id=user_id,
            name=vendor,
            category=first_receipt['category'],
            amount=round(avg_amount, 2),
            frequency="monthly",
            billing_day=billing_day,
            first_detected=first_receipt['date'],
            last_charge=last_receipt['date'],
            total_charges=len(receipts),
            total_spent=round(total_spent, 2),
            status=status,
            usage_estimate=usage
        )


# Global agent instance
_subscription_agent = None


def get_subscription_agent() -> SubscriptionAgent:
    """Get global subscription agent instance"""
    global _subscription_agent
    if _subscription_agent is None:
        _subscription_agent = SubscriptionAgent()
    return _subscription_agent
