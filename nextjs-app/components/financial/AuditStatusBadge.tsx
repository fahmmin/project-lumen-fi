import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface AuditStatusBadgeProps {
    status: 'pass' | 'warning' | 'error';
    className?: string;
}

export function AuditStatusBadge({ status, className }: AuditStatusBadgeProps) {
    const variants = {
        pass: 'success' as const,
        warning: 'warning' as const,
        error: 'error' as const,
    };

    return (
        <Badge variant={variants[status]} className={cn('uppercase', className)}>
            {status}
        </Badge>
    );
}

