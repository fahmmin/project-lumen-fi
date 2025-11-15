'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { web3Service } from '@/services/web3';

interface UserContextType {
    walletAddress: string | null;
    userId: string | null;
    isConnected: boolean;
    isLoading: boolean;
    connectWallet: () => Promise<void>;
    disconnectWallet: () => void;
    checkConnection: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

/**
 * Derives a user ID from wallet address
 * Uses the wallet address directly (lowercase) as user ID
 * This ensures consistency across the app
 */
function deriveUserIdFromAddress(address: string | null): string | null {
    if (!address) return null;
    // Use lowercase address as user ID for consistency
    // You could also hash it or use a different format if needed
    return address.toLowerCase();
}

export function UserProvider({ children }: { children: ReactNode }) {
    const [walletAddress, setWalletAddress] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Derive user ID from wallet address
    const userId = deriveUserIdFromAddress(walletAddress);
    const isConnected = !!walletAddress;

    const disconnectWallet = () => {
        setWalletAddress(null);
        localStorage.removeItem('walletAddress');
    };

    // Check for existing connection on mount
    useEffect(() => {
        checkConnection();

        // Listen for account changes
        if (typeof window !== 'undefined' && (window as any).ethereum) {
            const ethereum = (window as any).ethereum;
            const handleAccountsChanged = (accounts: string[]) => {
                if (accounts.length === 0) {
                    // User disconnected
                    disconnectWallet();
                } else {
                    // User switched accounts
                    setWalletAddress(accounts[0]);
                }
            };

            const handleChainChanged = () => {
                // Reload on chain change
                window.location.reload();
            };

            ethereum.on('accountsChanged', handleAccountsChanged);
            ethereum.on('chainChanged', handleChainChanged);

            return () => {
                ethereum?.removeListener('accountsChanged', handleAccountsChanged);
                ethereum?.removeListener('chainChanged', handleChainChanged);
            };
        }
    }, []);

    const checkConnection = async () => {
        try {
            setIsLoading(true);

            // First, check localStorage for saved address
            const savedAddress = localStorage.getItem('walletAddress');

            // Try to get address from MetaMask (silent check - doesn't require approval)
            if (typeof window !== 'undefined' && (window as any).ethereum) {
                try {
                    // Use eth_accounts which doesn't require user approval if previously connected
                    const accounts = await (window as any).ethereum.request({
                        method: 'eth_accounts'
                    });

                    if (accounts && accounts.length > 0) {
                        const currentAddress = accounts[0];
                        // If we have a saved address, verify it matches
                        if (savedAddress && savedAddress.toLowerCase() === currentAddress.toLowerCase()) {
                            // Restore connection
                            setWalletAddress(currentAddress);
                            // Reinitialize web3Service provider
                            try {
                                await web3Service.ensureSepoliaNetwork();
                            } catch (networkError) {
                                // Network switch failed, but we still have the address
                                console.log('Network switch failed, but address is available:', networkError);
                            }
                        } else if (!savedAddress) {
                            // No saved address but MetaMask has accounts - use the first one
                            setWalletAddress(currentAddress);
                            localStorage.setItem('walletAddress', currentAddress);
                        } else {
                            // Saved address doesn't match - user switched accounts
                            setWalletAddress(currentAddress);
                            localStorage.setItem('walletAddress', currentAddress);
                        }
                    } else if (savedAddress) {
                        // No accounts from MetaMask but we have saved address - clear it
                        localStorage.removeItem('walletAddress');
                        setWalletAddress(null);
                    }
                } catch (error) {
                    console.log('Error checking MetaMask accounts:', error);
                    // If eth_accounts fails, clear saved address
                    if (savedAddress) {
                        localStorage.removeItem('walletAddress');
                        setWalletAddress(null);
                    }
                }
            } else {
                // MetaMask not available
                if (savedAddress) {
                    localStorage.removeItem('walletAddress');
                    setWalletAddress(null);
                }
            }
        } catch (error) {
            console.error('Error in checkConnection:', error);
            // On error, clear saved address
            localStorage.removeItem('walletAddress');
            setWalletAddress(null);
        } finally {
            setIsLoading(false);
        }
    };

    const connectWallet = async () => {
        try {
            setIsLoading(true);
            // Ensure we're on Sepolia network
            await web3Service.ensureSepoliaNetwork();
            // Connect wallet
            const address = await web3Service.connectWallet();
            setWalletAddress(address);
            // Save to localStorage
            localStorage.setItem('walletAddress', address);

            // Auto-create user profile if it doesn't exist (unified flow)
            if (address) {
                try {
                    const userId = address.toLowerCase();
                    const { usersAPI } = await import('@/services/api');
                    // Try to get profile, if it fails, create it
                    await usersAPI.getProfile(userId).catch(async () => {
                        await usersAPI.createOrUpdateProfile({ user_id: userId });
                    });
                } catch (error) {
                    // Silently fail - profile creation is optional
                    console.log('Profile auto-creation skipped:', error);
                }
            }
        } catch (error: any) {
            throw new Error(error.message || 'Failed to connect wallet');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <UserContext.Provider
            value={{
                walletAddress,
                userId,
                isConnected,
                isLoading,
                connectWallet,
                disconnectWallet,
                checkConnection,
            }}
        >
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
}

