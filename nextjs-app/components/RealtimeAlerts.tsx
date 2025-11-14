'use client';

import { useEffect, useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertCircle, X, Bell, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

interface Alert {
    id: string;
    type: 'info' | 'warning' | 'error' | 'success';
    title: string;
    message: string;
    timestamp: Date;
}

interface RealtimeAlertsProps {
    userId: string;
    onClose?: () => void;
}

export function RealtimeAlerts({ userId, onClose }: RealtimeAlertsProps) {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [connected, setConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (!userId) return;

        const connect = () => {
            try {
                const wsUrl = process.env.NEXT_PUBLIC_WS_URL ||
                    (typeof window !== 'undefined'
                        ? `ws://${window.location.hostname}:8000/ws/alerts/${userId}`
                        : `ws://localhost:8000/ws/alerts/${userId}`);

                const ws = new WebSocket(wsUrl);

                ws.onopen = () => {
                    console.log('WebSocket connected');
                    setConnected(true);
                    if (reconnectTimeoutRef.current) {
                        clearTimeout(reconnectTimeoutRef.current);
                        reconnectTimeoutRef.current = null;
                    }
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);

                        if (data.type === 'alert' || data.type === 'notification') {
                            const newAlert: Alert = {
                                id: `${Date.now()}-${Math.random()}`,
                                type: data.alert_type || data.type || 'info',
                                title: data.title || 'Notification',
                                message: data.message || data.content || '',
                                timestamp: new Date(),
                            };

                            setAlerts((prev) => [newAlert, ...prev].slice(0, 10)); // Keep last 10 alerts
                        }
                    } catch (error) {
                        console.error('Failed to parse WebSocket message:', error);
                    }
                };

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    setConnected(false);
                };

                ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    setConnected(false);

                    // Reconnect after 5 seconds
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, 5000);
                };

                wsRef.current = ws;
            } catch (error) {
                console.error('Failed to connect WebSocket:', error);
                setConnected(false);
            }
        };

        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [userId]);

    const removeAlert = (id: string) => {
        setAlerts((prev) => prev.filter((alert) => alert.id !== id));
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'success':
                return <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />;
            case 'warning':
                return <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />;
            case 'error':
                return <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />;
            default:
                return <Info className="h-5 w-5 text-blue-600 dark:text-blue-400" />;
        }
    };

    if (alerts.length === 0 && !connected) {
        return null;
    }

    return (
        <Card className="fixed bottom-4 right-4 w-96 max-h-[600px] z-50 shadow-xl">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Bell className="h-5 w-5" />
                        <CardTitle className="text-lg">Real-time Alerts</CardTitle>
                    </div>
                    <div className="flex items-center gap-2">
                        <Badge variant={connected ? 'default' : 'secondary'}>
                            {connected ? 'Connected' : 'Disconnected'}
                        </Badge>
                        {onClose && (
                            <Button variant="ghost" size="sm" onClick={onClose}>
                                <X className="h-4 w-4" />
                            </Button>
                        )}
                    </div>
                </div>
                <CardDescription className="text-xs">
                    Live notifications and alerts
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 max-h-[500px] overflow-y-auto">
                {alerts.length === 0 ? (
                    <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-4">
                        No alerts yet. Alerts will appear here in real-time.
                    </p>
                ) : (
                    alerts.map((alert) => (
                        <div
                            key={alert.id}
                            className="p-3 border border-gray-200 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-gray-900"
                        >
                            <div className="flex items-start gap-2">
                                {getIcon(alert.type)}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1">
                                            <p className="font-semibold text-sm">{alert.title}</p>
                                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                                {alert.message}
                                            </p>
                                            <p className="text-xs text-gray-500 mt-1">
                                                {alert.timestamp.toLocaleTimeString()}
                                            </p>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => removeAlert(alert.id)}
                                            className="h-6 w-6 p-0"
                                        >
                                            <X className="h-3 w-3" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </CardContent>
        </Card>
    );
}

