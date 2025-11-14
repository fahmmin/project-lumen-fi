import { cn } from '@/lib/utils';

interface AmountDisplayProps {
    amount: number;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    className?: string;
}

export function AmountDisplay({
    amount,
    size = 'md',
    className,
}: AmountDisplayProps) {
    const sizeClasses = {
        sm: 'text-2xl',
        md: 'text-3xl',
        lg: 'text-4xl',
        xl: 'text-5xl',
    };

    return (
        <div className={cn('font-bold text-black dark:text-white', sizeClasses[size], className)}>
            ${amount.toFixed(2)}
        </div>
    );
}

