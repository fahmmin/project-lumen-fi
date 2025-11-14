import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

interface TransactionCardProps {
    vendor: string;
    date: string;
    amount: number;
    category?: string;
    invoiceNumber?: string;
    onClick?: () => void;
}

export function TransactionCard({
    vendor,
    date,
    amount,
    category,
    invoiceNumber,
    onClick,
}: TransactionCardProps) {
    return (
        <Card
            className={onClick ? 'cursor-pointer transition-shadow hover:shadow-md' : ''}
            onClick={onClick}
        >
            <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                    <CardTitle className="text-lg font-semibold">{vendor}</CardTitle>
                    <div className="text-right">
                        <div className="text-xl font-bold">${amount.toFixed(2)}</div>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span>{format(new Date(date), 'MMM dd, yyyy')}</span>
                    {category && (
                        <>
                            <span>•</span>
                            <Badge variant="outline">{category}</Badge>
                        </>
                    )}
                </div>
                {invoiceNumber && (
                    <div className="text-xs text-gray-500 dark:text-gray-500">
                        Invoice: {invoiceNumber}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

