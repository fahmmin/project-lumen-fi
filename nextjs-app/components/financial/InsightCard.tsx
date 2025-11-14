import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface InsightCardProps {
    title: string;
    description: string;
    type?: 'info' | 'warning' | 'success' | 'error';
    metadata?: Record<string, any>;
}

export function InsightCard({
    title,
    description,
    type = 'info',
    metadata,
}: InsightCardProps) {
    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{title}</CardTitle>
                    <Badge variant={type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'default'}>
                        {type}
                    </Badge>
                </div>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap mb-4">
                    {description}
                </p>
                {metadata && Object.keys(metadata).length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400">
                            {Object.entries(metadata).map(([key, value]) => (
                                <div key={key}>
                                    <span className="font-medium">{key}:</span> {String(value)}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

