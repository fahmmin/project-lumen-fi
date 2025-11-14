import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface ContainerProps {
    children: ReactNode;
    className?: string;
}

export function Container({ children, className }: ContainerProps) {
    return (
        <div className={cn(
            'container mx-auto px-4 sm:px-6 lg:px-8',
            'py-4 sm:py-6 lg:py-8',
            'max-w-7xl',
            className
        )}>
            {children}
        </div>
    );
}

