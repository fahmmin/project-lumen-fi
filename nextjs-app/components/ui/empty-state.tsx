import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
    title: string;
    description?: string;
    icon?: ReactNode;
    action?: ReactNode;
    className?: string;
}

export function EmptyState({
    title,
    description,
    icon,
    action,
    className,
}: EmptyStateProps) {
    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center py-12 px-4 text-center',
                className
            )}
        >
            {icon && <div className="mb-4 text-gray-400 dark:text-gray-600">{icon}</div>}
            <h3 className="text-lg font-semibold text-black dark:text-white mb-2">{title}</h3>
            {description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 max-w-md mb-4">{description}</p>
            )}
            {action && <div>{action}</div>}
        </div>
    );
}

