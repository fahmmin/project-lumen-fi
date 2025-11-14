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
        <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-black">
            <div className="container mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                    <Link href="/" className="text-xl font-bold text-black dark:text-white">
                        LUMEN
                    </Link>
                    <div className="flex items-center gap-4">
                        <nav className="hidden md:flex items-center gap-6">
                            {navItems.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        'text-sm font-medium transition-colors hover:text-black dark:hover:text-white',
                                        pathname === item.href
                                            ? 'text-black dark:text-white'
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

