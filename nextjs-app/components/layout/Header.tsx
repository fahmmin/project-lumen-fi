'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/theme-toggle';
import {
    Menu, X, Trophy, Flame, LayoutDashboard, Upload, FileText,
    ShieldCheck, DollarSign, Target, Bell, CreditCard, Heart,
    TrendingUp, Search, FileBarChart, Users, Gamepad2, Home,
    Mic, Mail, Store, Eye, MessageCircle, Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUser } from '@/contexts/UserContext';
import { gamificationAPI } from '@/services/api';
import { Skeleton } from '@/components/ui/skeleton';

// Navigation items with icons and colors
const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, color: 'text-blue-600 dark:text-blue-400' },
    { href: '/assistant', label: 'Assistant', icon: MessageCircle, color: 'text-purple-600 dark:text-purple-400' },
    { href: '/upload', label: 'Upload', icon: Upload, color: 'text-green-600 dark:text-green-400' },
    { href: '/audit', label: 'Audit', icon: ShieldCheck, color: 'text-red-600 dark:text-red-400' },
    { href: '/goals', label: 'Goals', icon: Target, color: 'text-orange-600 dark:text-orange-400' },
    { href: '/forensics', label: 'Forensics', icon: Search, color: 'text-cyan-600 dark:text-cyan-400' },

    { href: '/family', label: 'Family', icon: Home, color: 'text-teal-600 dark:text-teal-400' },
    { href: '/gamification', label: 'Gamification', icon: Gamepad2, color: 'text-amber-600 dark:text-amber-400' },
    { href: '/documents', label: 'Documents', icon: FileText, color: 'text-gray-600 dark:text-gray-400' },
    { href: '/email', label: 'Email', icon: Mail, color: 'text-blue-500 dark:text-blue-300' },
    { href: '/store', label: 'Store', icon: Store, color: 'text-fuchsia-600 dark:text-fuchsia-400' },

    { href: '/finance', label: 'Finance', icon: DollarSign, color: 'text-emerald-600 dark:text-emerald-400' },
    { href: '/reminders', label: 'Reminders', icon: Bell, color: 'text-yellow-600 dark:text-yellow-400' },
    { href: '/subscriptions', label: 'Subscriptions', icon: CreditCard, color: 'text-pink-600 dark:text-pink-400' },
    { href: '/health', label: 'Health', icon: Heart, color: 'text-rose-600 dark:text-rose-400' },
    { href: '/insights', label: 'Insights', icon: TrendingUp, color: 'text-indigo-600 dark:text-indigo-400' },
    { href: '/reports', label: 'Reports', icon: FileBarChart, color: 'text-violet-600 dark:text-violet-400' },
    { href: '/social', label: 'Social', icon: Users, color: 'text-sky-600 dark:text-sky-400' },
    { href: '/voice', label: 'Voice', icon: Mic, color: 'text-lime-600 dark:text-lime-400' },
    { href: '/view', label: 'View', icon: Eye, color: 'text-slate-600 dark:text-slate-400' },
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
        <header className="sticky top-0 z-40 border-b border-gray-200 dark:border-gray-800 bg-white/95 dark:bg-black/95 backdrop-blur-lg shadow-sm">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
                <div className="flex h-14 sm:h-16 items-center justify-between">
                    <Link
                        href="/"
                        className="flex items-center gap-2 sm:gap-3 group hover:opacity-90 transition-all duration-200"
                    >
                        <div className="relative w-8 h-8 sm:w-10 sm:h-10 flex-shrink-0">
                            <Image
                                src="/lumenlogo.svg"
                                alt="LUMEN Logo"
                                fill
                                className="object-contain group-hover:scale-110 transition-transform duration-200"
                                priority
                            />
                        </div>
                        <span className="text-lg sm:text-xl font-bold text-black dark:text-white tracking-tight">
                            LUMEN
                        </span>
                    </Link>
                    <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0 justify-end lg:justify-between">
                        {/* Desktop Navigation - Scrollable horizontal menu with all items visible */}
                        <nav className="hidden lg:flex items-center gap-1 xl:gap-1.5 overflow-x-auto scrollbar-hide flex-1 min-w-0 px-2">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                const isActive = pathname === item.href;
                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        className={cn(
                                            'flex items-center gap-1.5 text-xs xl:text-sm font-medium transition-all duration-200 px-3 py-1.5 rounded-lg whitespace-nowrap flex-shrink-0 group',
                                            isActive
                                                ? 'bg-black dark:bg-white text-white dark:text-black shadow-sm'
                                                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:scale-105'
                                        )}
                                        title={item.label}
                                    >
                                        <Icon className={cn(
                                            'h-4 w-4 transition-colors duration-200',
                                            isActive ? 'text-white dark:text-black' : 'text-gray-500 dark:text-gray-400 group-hover:text-black dark:group-hover:text-white'
                                        )} />
                                        <span>{item.label}</span>
                                    </Link>
                                );
                            })}
                        </nav>

                        {/* Right side items */}
                        <div className="flex items-center gap-2 sm:gap-3">
                            {/* Gamification Stats - Desktop */}
                            {isConnected && (
                                <div className="hidden md:flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 flex-shrink-0 shadow-sm">
                                    {loadingStats ? (
                                        <>
                                            <Skeleton className="h-4 w-10" />
                                            <Skeleton className="h-4 w-12" />
                                        </>
                                    ) : gamificationStats ? (
                                        <>
                                            <Link
                                                href="/gamification"
                                                className="flex items-center gap-1.5 hover:opacity-80 transition-all hover:scale-105 cursor-pointer group"
                                                title="View gamification details"
                                            >
                                                <Trophy className="h-4 w-4 text-black dark:text-white group-hover:animate-bounce" />
                                                <span className="text-xs font-bold text-black dark:text-white">
                                                    L{gamificationStats.level || 1}
                                                </span>
                                            </Link>
                                            <div className="h-4 w-px bg-gray-300 dark:bg-gray-700" />
                                            <Link
                                                href="/gamification"
                                                className="flex items-center gap-1 text-xs font-semibold hover:opacity-80 transition-all hover:scale-105 cursor-pointer"
                                                title="Total points"
                                            >
                                                <Sparkles className="h-3 w-3 text-black dark:text-white" />
                                                <span className="text-gray-700 dark:text-gray-300">
                                                    {(gamificationStats.total_points || 0).toLocaleString()}
                                                </span>
                                            </Link>
                                            {gamificationStats.current_streak > 0 && (
                                                <>
                                                    <div className="h-4 w-px bg-gray-300 dark:bg-gray-700" />
                                                    <Link
                                                        href="/gamification"
                                                        className="flex items-center gap-1 text-xs font-semibold hover:opacity-80 transition-all hover:scale-105 cursor-pointer group"
                                                        title="Current streak"
                                                    >
                                                        <Flame className="h-3.5 w-3.5 text-black dark:text-white group-hover:animate-pulse" />
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
                                <div className="md:hidden flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 flex-shrink-0 shadow-sm">
                                    {loadingStats ? (
                                        <Skeleton className="h-4 w-10" />
                                    ) : gamificationStats ? (
                                        <Link
                                            href="/gamification"
                                            className="flex items-center gap-1 hover:opacity-80 transition-all hover:scale-105"
                                            title="Gamification"
                                        >
                                            <Trophy className="h-3.5 w-3.5 text-black dark:text-white" />
                                            <span className="text-xs font-bold text-black dark:text-white">
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
                    <nav className="lg:hidden border-t border-gray-200 dark:border-gray-800 py-4 max-h-[calc(100vh-4rem)] overflow-y-auto bg-white dark:bg-black">
                        <div className="grid grid-cols-2 gap-2">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                const isActive = pathname === item.href;
                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        className={cn(
                                            'flex items-center gap-2 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200',
                                            isActive
                                                ? 'bg-black dark:bg-white text-white dark:text-black shadow-sm'
                                                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 active:scale-95'
                                        )}
                                        onClick={() => setMobileMenuOpen(false)}
                                    >
                                        <Icon className={cn(
                                            'h-4 w-4 flex-shrink-0',
                                            isActive ? 'text-white dark:text-black' : 'text-gray-500 dark:text-gray-400'
                                        )} />
                                        <span>{item.label}</span>
                                    </Link>
                                );
                            })}
                        </div>
                    </nav>
                )}
            </div>
        </header>
    );
}

