'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, FileSearch, Database, TrendingUp, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
    href: string;
    icon: React.ComponentType<{ className?: string }>;
    label: string;
}

const navItems: NavItem[] = [
    { href: '/dashboard', icon: Home, label: 'Home' },
    { href: '/audit', icon: FileSearch, label: 'Audit' },
    { href: '/documents', icon: Database, label: 'Documents' },
    { href: '/insights', icon: TrendingUp, label: 'Insights' },
];

export function BottomNavigation() {
    const pathname = usePathname();

    return (
        <>
            {/* Mobile bottom navigation */}
            <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-lg border-t border-gray-200/50 dark:border-gray-800/50 safe-area-inset-bottom shadow-lg">
                {/* Curved top border effect */}
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-gray-700 to-transparent" />

                <div className="max-w-md mx-auto px-2 pb-2 pt-2">
                    <div className="flex items-center justify-around relative">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = pathname === item.href ||
                                (item.href === '/dashboard' && pathname === '/');

                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "flex flex-col items-center justify-center gap-1 px-3 py-2 rounded-xl transition-all duration-200 relative",
                                        "min-w-[56px] active:scale-95",
                                        isActive
                                            ? "text-black dark:text-white"
                                            : "text-gray-500 dark:text-gray-400"
                                    )}
                                >
                                    {isActive && (
                                        <div className="absolute inset-0 bg-gray-100 dark:bg-gray-800 rounded-xl -z-10" />
                                    )}
                                    <Icon
                                        className={cn(
                                            "h-5 w-5 transition-transform duration-200",
                                            isActive && "scale-110"
                                        )}
                                    />
                                    <span className={cn(
                                        "text-[10px] font-medium transition-all duration-200 leading-tight",
                                        isActive ? "opacity-100" : "opacity-70"
                                    )}>
                                        {item.label}
                                    </span>
                                </Link>
                            );
                        })}

                        {/* Central action button with curved effect */}
                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-20 h-1">
                            <div className="absolute inset-0 bg-gradient-to-t from-gray-200/50 dark:from-gray-700/50 to-transparent rounded-t-full" />
                        </div>
                        <Link
                            href="/upload"
                            className="flex items-center justify-center w-14 h-14 rounded-full bg-black dark:bg-white text-white dark:text-black shadow-xl hover:shadow-2xl transition-all duration-200 -mt-7 relative z-10 active:scale-95"
                        >
                            <Plus className="h-6 w-6" />
                        </Link>
                    </div>
                </div>
            </nav>
        </>
    );
}

