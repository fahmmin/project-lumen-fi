'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/theme-toggle';

const navItems = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/upload', label: 'Upload' },
    { href: '/documents', label: 'Documents' },
    { href: '/audit', label: 'Audit' },
    { href: '/finance', label: 'Finance' },
    { href: '/goals', label: 'Goals' },
    { href: '/reminders', label: 'Reminders' },
    { href: '/subscriptions', label: 'Subscriptions' },
    { href: '/forensics', label: 'Forensics' },
    { href: '/health', label: 'Health' },
    { href: '/insights', label: 'Insights' },
    { href: '/store', label: 'Store' },
    { href: '/view', label: 'View' },
];

export function Header() {
    const pathname = usePathname();

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
                    <div className="flex items-center gap-3 sm:gap-4">
                        <nav className="hidden lg:flex items-center gap-4 xl:gap-6">
                            {navItems.slice(0, 6).map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        'text-xs xl:text-sm font-medium transition-colors hover:text-black dark:hover:text-white px-2 py-1 rounded-md',
                                        pathname === item.href
                                            ? 'text-black dark:text-white bg-gray-100 dark:bg-gray-900'
                                            : 'text-gray-600 dark:text-gray-400'
                                    )}
                                >
                                    {item.label}
                                </Link>
                            ))}
                        </nav>
                        <ThemeToggle />
                    </div>
                </div>
            </div>
        </header>
    );
}

