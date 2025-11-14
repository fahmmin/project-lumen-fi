'use client';

import { useEffect } from 'react';

interface NotificationProps {
    message: string;
    type: 'success' | 'error' | 'info';
    onClose: () => void;
    duration?: number;
}

export default function Notification({
    message,
    type,
    onClose,
    duration = 5000,
}: NotificationProps) {
    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                onClose();
            }, duration);
            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    const bgColors = {
        success: 'bg-green-100 border-green-500 text-green-800',
        error: 'bg-red-100 border-red-500 text-red-800',
        info: 'bg-blue-100 border-blue-500 text-blue-800',
    };

    return (
        <div
            className={`fixed top-4 right-4 px-6 py-4 rounded-lg border-2 ${bgColors[type]} shadow-lg z-50 max-w-md`}
        >
            <div className="flex items-center justify-between gap-4">
                <p className="font-medium">{message}</p>
                <button
                    onClick={onClose}
                    className="text-gray-600 hover:text-gray-800 font-bold text-xl"
                >
                    ×
                </button>
            </div>
        </div>
    );
}

