"""
Alert Manager - Manages real-time alerts and notifications
"""

from typing import List, Optional, Dict
import json
import os
import uuid
from datetime import datetime

from backend.models.alert import Alert, AlertType, AlertSeverity, FraudAlert, BudgetAlert, AchievementAlert
from backend.utils.logger import logger


class AlertManager:
    """Manages user alerts and real-time notifications"""

    def __init__(self):
        self.data_dir = "backend/data/alerts"
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_user_alerts_file(self, user_id: str) -> str:
        """Get path to user's alerts file"""
        return os.path.join(self.data_dir, f"{user_id}_alerts.json")

    def _load_alerts(self, user_id: str) -> List[Dict]:
        """Load user's alerts"""
        file_path = self._get_user_alerts_file(user_id)

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)

        return []

    def _save_alerts(self, user_id: str, alerts: List[Dict]):
        """Save user's alerts"""
        file_path = self._get_user_alerts_file(user_id)

        with open(file_path, 'w') as f:
            json.dump(alerts, f, indent=2)

    def create_alert(self, alert: Alert) -> Alert:
        """Create and store a new alert"""
        # Generate ID if not present
        if not hasattr(alert, 'alert_id') or not alert.alert_id:
            alert.alert_id = f"alert_{uuid.uuid4().hex[:12]}"

        # Load existing alerts
        alerts = self._load_alerts(alert.user_id)

        # Add new alert
        alert_dict = alert.model_dump()
        alert_dict['timestamp'] = alert_dict['timestamp'].isoformat()
        alerts.insert(0, alert_dict)  # Most recent first

        # Keep only last 100 alerts
        alerts = alerts[:100]

        # Save
        self._save_alerts(alert.user_id, alerts)

        logger.info(f"Created alert {alert.alert_id} for user {alert.user_id}: {alert.type}")

        return alert

    def create_fraud_alert(
        self,
        user_id: str,
        transaction_id: str,
        fraud_score: float,
        fraud_indicators: List[str],
        amount: float,
        vendor: str
    ) -> FraudAlert:
        """Create a fraud alert"""
        alert = FraudAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            title="🚨 Potential Fraud Detected",
            message=f"Suspicious transaction detected at {vendor} for ${amount:.2f}. Fraud score: {fraud_score:.0%}",
            fraud_score=fraud_score,
            fraud_indicators=fraud_indicators,
            transaction_id=transaction_id,
            amount=amount,
            vendor=vendor,
            data={
                "fraud_score": fraud_score,
                "indicators": fraud_indicators,
                "transaction_id": transaction_id
            },
            action_url=f"/transactions/{transaction_id}"
        )

        return self.create_alert(alert)

    def create_budget_alert(
        self,
        user_id: str,
        category: str,
        spent: float,
        budget_limit: float,
        exceeded: bool = False
    ) -> BudgetAlert:
        """Create a budget warning or exceeded alert"""
        percentage = (spent / budget_limit) * 100 if budget_limit > 0 else 0

        if exceeded:
            alert_type = AlertType.BUDGET_EXCEEDED
            severity = AlertSeverity.WARNING
            title = f"⚠️ Budget Exceeded: {category.title()}"
            message = f"You've exceeded your {category} budget by ${spent - budget_limit:.2f} ({percentage:.0f}%)"
        else:
            alert_type = AlertType.BUDGET_WARNING
            severity = AlertSeverity.WARNING
            title = f"⚠️ Budget Alert: {category.title()}"
            message = f"You've used {percentage:.0f}% of your {category} budget (${spent:.2f} / ${budget_limit:.2f})"

        alert = BudgetAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            category=category,
            spent=spent,
            budget_limit=budget_limit,
            percentage_used=percentage,
            data={
                "category": category,
                "spent": spent,
                "budget": budget_limit,
                "percentage": percentage
            }
        )

        return self.create_alert(alert)

    def create_achievement_alert(
        self,
        user_id: str,
        badge_name: str,
        badge_icon: str,
        points_earned: int
    ) -> AchievementAlert:
        """Create an achievement unlocked alert"""
        alert = AchievementAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            title=f"🎉 Achievement Unlocked!",
            message=f"You earned the '{badge_name}' badge! +{points_earned} points",
            badge_name=badge_name,
            badge_icon=badge_icon,
            points_earned=points_earned,
            data={
                "badge": badge_name,
                "icon": badge_icon,
                "points": points_earned
            }
        )

        return self.create_alert(alert)

    def create_custom_alert(
        self,
        user_id: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> Alert:
        """Create a custom alert"""
        alert = Alert(
            alert_id=f"alert_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            data=data
        )

        return self.create_alert(alert)

    def get_user_alerts(
        self,
        user_id: str,
        unread_only: bool = False,
        alert_type: Optional[AlertType] = None,
        limit: int = 50
    ) -> List[Alert]:
        """Get user's alerts with filters"""
        alerts = self._load_alerts(user_id)

        # Filter unread
        if unread_only:
            alerts = [a for a in alerts if not a.get('read', False)]

        # Filter by type
        if alert_type:
            alerts = [a for a in alerts if a.get('type') == alert_type]

        # Limit
        alerts = alerts[:limit]

        # Convert to Alert objects
        alert_objects = []
        for alert_dict in alerts:
            # Convert timestamp back to datetime
            if isinstance(alert_dict.get('timestamp'), str):
                alert_dict['timestamp'] = datetime.fromisoformat(alert_dict['timestamp'])

            # Create appropriate alert type
            if alert_dict.get('type') == AlertType.FRAUD:
                alert_objects.append(FraudAlert(**alert_dict))
            elif alert_dict.get('type') in [AlertType.BUDGET_WARNING, AlertType.BUDGET_EXCEEDED]:
                alert_objects.append(BudgetAlert(**alert_dict))
            elif alert_dict.get('type') == AlertType.ACHIEVEMENT:
                alert_objects.append(AchievementAlert(**alert_dict))
            else:
                alert_objects.append(Alert(**alert_dict))

        return alert_objects

    def mark_as_read(self, user_id: str, alert_id: str) -> bool:
        """Mark an alert as read"""
        alerts = self._load_alerts(user_id)

        found = False
        for alert in alerts:
            if alert.get('alert_id') == alert_id:
                alert['read'] = True
                found = True
                break

        if found:
            self._save_alerts(user_id, alerts)
            logger.info(f"Marked alert {alert_id} as read for user {user_id}")

        return found

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all alerts as read"""
        alerts = self._load_alerts(user_id)

        count = 0
        for alert in alerts:
            if not alert.get('read', False):
                alert['read'] = True
                count += 1

        self._save_alerts(user_id, alerts)
        logger.info(f"Marked {count} alerts as read for user {user_id}")

        return count

    def delete_alert(self, user_id: str, alert_id: str) -> bool:
        """Delete an alert"""
        alerts = self._load_alerts(user_id)

        original_count = len(alerts)
        alerts = [a for a in alerts if a.get('alert_id') != alert_id]

        if len(alerts) < original_count:
            self._save_alerts(user_id, alerts)
            logger.info(f"Deleted alert {alert_id} for user {user_id}")
            return True

        return False

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread alerts"""
        alerts = self._load_alerts(user_id)
        return sum(1 for a in alerts if not a.get('read', False))


# Global instance
alert_manager = AlertManager()
