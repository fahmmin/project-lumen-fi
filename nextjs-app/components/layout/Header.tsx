'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/theme-toggle';
import { Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

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
                    <div className="flex items-center gap-3 sm:gap-4 flex-1 min-w-0">
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

                        <ThemeToggle />
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

