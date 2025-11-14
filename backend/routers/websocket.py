"""
WebSocket API - Real-time Alerts and Notifications
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime

from backend.models.alert import Alert, AlertType, AlertSeverity
from backend.utils.alert_manager import alert_manager
from backend.utils.logger import logger

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections for real-time alerts"""

    def __init__(self):
        # user_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            if len(self.active_connections[user_id]) == 0:
                del self.active_connections[user_id]

        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, message: str, user_id: str):
        """Send message to specific user's connections"""
        if user_id in self.active_connections:
            disconnected = []

            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast_alert(self, alert: Alert):
        """Broadcast alert to user's connections"""
        alert_dict = alert.model_dump()
        alert_dict['timestamp'] = alert_dict['timestamp'].isoformat()

        message = json.dumps({
            "type": "alert",
            "data": alert_dict
        })

        await self.send_personal_message(message, alert.user_id)

    def get_connection_count(self, user_id: str) -> int:
        """Get number of active connections for user"""
        return len(self.active_connections.get(user_id, []))


# Global connection manager
manager = ConnectionManager()


@router.websocket("/alerts/{user_id}")
async def websocket_alerts(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time alerts

    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/alerts/test_user_001');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'alert') {
            console.log('Alert:', data.data);
            // Show notification to user
        }
    };
    ```
    """
    await manager.connect(websocket, user_id)

    try:
        # Send initial connection success message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to real-time alerts",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })

        # Send unread count
        unread_count = alert_manager.get_unread_count(user_id)
        await websocket.send_json({
            "type": "unread_count",
            "count": unread_count
        })

        # Keep connection alive
        while True:
            # Receive messages from client (heartbeat, mark as read, etc.)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)

                # Handle client messages
                if message.get("type") == "mark_read":
                    alert_id = message.get("alert_id")
                    if alert_id:
                        alert_manager.mark_as_read(user_id, alert_id)
                        await websocket.send_json({
                            "type": "marked_read",
                            "alert_id": alert_id
                        })

                elif message.get("type") == "mark_all_read":
                    count = alert_manager.mark_all_as_read(user_id)
                    await websocket.send_json({
                        "type": "all_marked_read",
                        "count": count
                    })

                elif message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })

            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


# HTTP endpoints for alerts
from fastapi import APIRouter as HTTPRouter

alerts_router = HTTPRouter(prefix="/alerts", tags=["Alerts"])


@alerts_router.get("/{user_id}")
async def get_user_alerts(
    user_id: str,
    unread_only: bool = Query(False, description="Get only unread alerts"),
    alert_type: Optional[AlertType] = Query(None, description="Filter by alert type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of alerts")
):
    """
    Get user's alerts

    **Parameters:**
    - unread_only: Return only unread alerts
    - alert_type: Filter by specific alert type
    - limit: Maximum number of alerts to return
    """
    try:
        alerts = alert_manager.get_user_alerts(
            user_id=user_id,
            unread_only=unread_only,
            alert_type=alert_type,
            limit=limit
        )

        return {
            "user_id": user_id,
            "alerts": alerts,
            "count": len(alerts)
        }

    except Exception as e:
        logger.error(f"Error getting alerts for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@alerts_router.get("/{user_id}/unread-count")
async def get_unread_count(user_id: str):
    """Get count of unread alerts"""
    try:
        count = alert_manager.get_unread_count(user_id)
        return {
            "user_id": user_id,
            "unread_count": count
        }

    except Exception as e:
        logger.error(f"Error getting unread count for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@alerts_router.post("/{user_id}/mark-read/{alert_id}")
async def mark_alert_as_read(user_id: str, alert_id: str):
    """Mark specific alert as read"""
    try:
        success = alert_manager.mark_as_read(user_id, alert_id)

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {
            "success": True,
            "alert_id": alert_id,
            "message": "Alert marked as read"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking alert as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@alerts_router.post("/{user_id}/mark-all-read")
async def mark_all_alerts_as_read(user_id: str):
    """Mark all alerts as read"""
    try:
        count = alert_manager.mark_all_as_read(user_id)

        return {
            "success": True,
            "marked_count": count,
            "message": f"Marked {count} alerts as read"
        }

    except Exception as e:
        logger.error(f"Error marking all alerts as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@alerts_router.delete("/{user_id}/alerts/{alert_id}")
async def delete_alert(user_id: str, alert_id: str):
    """Delete specific alert"""
    try:
        success = alert_manager.delete_alert(user_id, alert_id)

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {
            "success": True,
            "alert_id": alert_id,
            "message": "Alert deleted"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Test endpoint to trigger alerts
@alerts_router.post("/{user_id}/test-alert")
async def trigger_test_alert(user_id: str, alert_type: AlertType = Query(AlertType.FRAUD)):
    """
    Trigger a test alert (for development/demo)

    **Alert Types:**
    - fraud: Fraud detection alert
    - budget_warning: Budget warning
    - achievement: Achievement unlocked
    """
    try:
        if alert_type == AlertType.FRAUD:
            alert = alert_manager.create_fraud_alert(
                user_id=user_id,
                transaction_id="txn_test_123",
                fraud_score=0.87,
                fraud_indicators=["Unusual vendor", "High amount", "Irregular time"],
                amount=599.99,
                vendor="Suspicious Store Inc."
            )

        elif alert_type == AlertType.BUDGET_WARNING:
            alert = alert_manager.create_budget_alert(
                user_id=user_id,
                category="dining",
                spent=425.0,
                budget_limit=400.0,
                exceeded=True
            )

        elif alert_type == AlertType.ACHIEVEMENT:
            alert = alert_manager.create_achievement_alert(
                user_id=user_id,
                badge_name="Week Warrior",
                badge_icon="🔥",
                points_earned=50
            )

        else:
            alert = alert_manager.create_custom_alert(
                user_id=user_id,
                alert_type=alert_type,
                severity=AlertSeverity.INFO,
                title="Test Alert",
                message="This is a test alert"
            )

        # Broadcast to WebSocket connections
        await manager.broadcast_alert(alert)

        return {
            "success": True,
            "alert": alert,
            "message": "Test alert created and broadcasted"
        }

    except Exception as e:
        logger.error(f"Error creating test alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include both routers
router.include_router(alerts_router)
