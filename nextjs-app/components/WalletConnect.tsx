'use client';

import { useState, useEffect } from 'react';
import { web3Service } from '@/services/web3';

interface WalletConnectProps {
    onConnect?: (address: string) => void;
    onDisconnect?: () => void;
}

export default function WalletConnect({ onConnect, onDisconnect }: WalletConnectProps) {
    const [address, setAddress] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        checkConnection();
    }, []);

    const checkConnection = async () => {
        try {
            const addr = await web3Service.getAddress();
            if (addr) {
                setAddress(addr);
                onConnect?.(addr);
            }
        } catch (err) {
            // Not connected
        }
    };

    const handleConnect = async () => {
        setLoading(true);
        setError(null);
        try {
            // This will open MetaMask and switch to Sepolia if needed
            const addr = await web3Service.connectWallet();
            setAddress(addr);
            onConnect?.(addr);
        } catch (err: any) {
            setError(err.message || 'Failed to connect wallet');
        } finally {
            setLoading(false);
        }
    };

    const handleDisconnect = () => {
        setAddress(null);
        onDisconnect?.();
    };

    const formatAddress = (addr: string) => {
        return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
    };

    if (address) {
        return (
            <div className="flex items-center gap-4">
                <div className="px-4 py-2 bg-green-100 text-green-800 rounded-lg">
                    <span className="text-sm font-medium">Connected: {formatAddress(address)}</span>
                </div>
                <button
                    onClick={handleDisconnect}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                    Disconnect
                </button>
            </div>
        );
    }

    return (
        <div>
            <button
                onClick={handleConnect}
                disabled={loading}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
                {loading ? 'Connecting...' : 'Connect Wallet'}
            </button>
            {error && (
                <p className="mt-2 text-sm text-red-600">{error}</p>
            )}
        </div>
    );
}

