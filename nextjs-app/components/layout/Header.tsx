'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/theme-toggle';
import { Menu, X, Trophy, Flame } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUser } from '@/contexts/UserContext';
import { gamificationAPI } from '@/services/api';
import { Skeleton } from '@/components/ui/skeleton';

// Grouped navigation items - merge similar features
const navItems = [
    { href: '/dashboard', label: 'Dashboard', group: 'main' },
    { href: '/upload', label: 'Upload', group: 'main' },
    { href: '/documents', label: 'Documents', group: 'main' },
    { href: '/audit', label: 'Audit', group: 'main' },
    { href: '/finance', label: 'Finance', group: 'financial' },
    { href: '/goals', label: 'Goals', group: 'financial' },
    { href: '/reminders', label: 'Reminders', group: 'financial' },
    { href: '/subscriptions', label: 'Subscriptions', group: 'financial' },
    { href: '/health', label: 'Health', group: 'financial' },
    { href: '/insights', label: 'Insights', group: 'analytics' },
    { href: '/forensics', label: 'Forensics', group: 'analytics' },
    { href: '/reports', label: 'Reports', group: 'analytics' },
    { href: '/social', label: 'Social', group: 'social' },
    { href: '/gamification', label: 'Gamification', group: 'social' },
    { href: '/family', label: 'Family', group: 'social' },
    { href: '/voice', label: 'Voice', group: 'input' },
    { href: '/email', label: 'Email', group: 'input' },
    { href: '/store', label: 'Store', group: 'blockchain' },
    { href: '/view', label: 'View', group: 'blockchain' },
];

export function Header() {
    const pathname = usePathname();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const { userId, isConnected } = useUser();
    const [gamificationStats, setGamificationStats] = useState<any>(null);
    const [loadingStats, setLoadingStats] = useState(false);

    // Fetch gamification stats when user is connected
    useEffect(() => {
        const loadStats = async () => {
            if (!userId || !isConnected) {
                setGamificationStats(null);
                return;
            }
            setLoadingStats(true);
            try {
                const stats = await gamificationAPI.getUserStats(userId);
                setGamificationStats(stats);
            } catch (error) {
                // Silently fail - gamification is optional
                console.log('Failed to load gamification stats:', error);
            } finally {
                setLoadingStats(false);
            }
        };
        loadStats();
    }, [userId, isConnected]);

    return (
        <header className="sticky top-0 z-40 border-b border-gray-200/50 dark:border-gray-800/50 bg-white/95 dark:bg-black/95 backdrop-blur-lg">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
                <div className="flex h-14 sm:h-16 items-center justify-between">
                    <Link
                        href="/"
                        className="text-lg sm:text-xl font-bold text-black dark:text-white tracking-tight hover:opacity-80 transition-opacity"
                    >
                        LUMEN
                    </Link>
                    <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0 justify-end lg:justify-between">
                        {/* Desktop Navigation - Scrollable horizontal menu with all items visible */}
                        <nav className="hidden lg:flex items-center gap-1 xl:gap-2 overflow-x-auto scrollbar-hide flex-1 min-w-0">
                            {navItems.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        'text-xs xl:text-sm font-medium transition-colors hover:text-black dark:hover:text-white px-2 py-1 rounded-md whitespace-nowrap flex-shrink-0',
                                        pathname === item.href
                                            ? 'text-black dark:text-white bg-gray-100 dark:bg-gray-900'
                                            : 'text-gray-600 dark:text-gray-400'
                                    )}
                                >
                                    {item.label}
                                </Link>
                            ))}
                        </nav>

                        {/* Right side items */}
                        <div className="flex items-center gap-2 sm:gap-3">
                            {/* Gamification Stats - Desktop */}
                            {isConnected && (
                                <div className="hidden md:flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 flex-shrink-0">
                                    {loadingStats ? (
                                        <>
                                            <Skeleton className="h-4 w-10" />
                                            <Skeleton className="h-4 w-12" />
                                        </>
                                    ) : gamificationStats ? (
                                        <>
                                            <Link
                                                href="/gamification"
                                                className="flex items-center gap-1.5 hover:opacity-80 transition-opacity cursor-pointer"
                                                title="View gamification details"
                                            >
                                                <Trophy className="h-4 w-4 text-yellow-600 dark:text-yellow-500" />
                                                <span className="text-xs font-semibold">
                                                    L{gamificationStats.level || 1}
                                                </span>
                                            </Link>
                                            <div className="h-4 w-px bg-gray-300 dark:bg-gray-700" />
                                            <Link
                                                href="/gamification"
                                                className="flex items-center gap-1 text-xs font-medium hover:opacity-80 transition-opacity cursor-pointer"
                                                title="Total points"
                                            >
                                                <span className="text-gray-700 dark:text-gray-300">
                                                    {(gamificationStats.total_points || 0).toLocaleString()}
                                                </span>
                                            </Link>
                                            {gamificationStats.current_streak > 0 && (
                                                <>
                                                    <div className="h-4 w-px bg-gray-300 dark:bg-gray-700" />
                                                    <Link
                                                        href="/gamification"
                                                        className="flex items-center gap-1 text-xs font-medium hover:opacity-80 transition-opacity cursor-pointer"
                                                        title="Current streak"
                                                    >
                                                        <Flame className="h-3.5 w-3.5 text-orange-500" />
                                                        <span className="text-gray-700 dark:text-gray-300">
                                                            {gamificationStats.current_streak}
                                                        </span>
                                                    </Link>
                                                </>
                                            )}
                                        </>
                                    ) : null}
                                </div>
                            )}

                            {/* Mobile Menu Button */}
                            <Button
                                variant="ghost"
                                size="sm"
                                className="lg:hidden"
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            >
                                {mobileMenuOpen ? (
                                    <X className="h-5 w-5" />
                                ) : (
                                    <Menu className="h-5 w-5" />
                                )}
                            </Button>

                            {/* Gamification Stats - Mobile (compact) */}
                            {isConnected && !mobileMenuOpen && (
                                <div className="md:hidden flex items-center gap-1.5 px-2 py-1 rounded bg-gray-100 dark:bg-gray-900 flex-shrink-0">
                                    {loadingStats ? (
                                        <Skeleton className="h-4 w-10" />
                                    ) : gamificationStats ? (
                                        <Link
                                            href="/gamification"
                                            className="flex items-center gap-1 hover:opacity-80 transition-opacity"
                                            title="Gamification"
                                        >
                                            <Trophy className="h-3.5 w-3.5 text-yellow-600 dark:text-yellow-500" />
                                            <span className="text-xs font-semibold">
                                                {(gamificationStats.total_points || 0).toLocaleString()}
                                            </span>
                                        </Link>
                                    ) : null}
                                </div>
                            )}

                            <ThemeToggle />
                        </div>
                    </div>
                </div>

                {/* Mobile Navigation Menu */}
                {mobileMenuOpen && (
                    <nav className="lg:hidden border-t border-gray-200 dark:border-gray-800 py-4 max-h-[calc(100vh-4rem)] overflow-y-auto">
                        <div className="grid grid-cols-2 gap-2">
                            {navItems.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        'px-3 py-2 text-sm font-medium rounded-md transition-colors',
                                        pathname === item.href
                                            ? 'text-black dark:text-white bg-gray-100 dark:bg-gray-900'
                                            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-950'
                                    )}
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    {item.label}
                                </Link>
                            ))}
                        </div>
                    </nav>
                )}
            </div>
        </header>
    );
}

