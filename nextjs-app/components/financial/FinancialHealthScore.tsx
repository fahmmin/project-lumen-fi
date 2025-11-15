'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Heart, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { useUser } from '@/contexts/UserContext';
import { generateWithGemini, generateSeededData } from '@/lib/geminiDataGenerator';

interface HealthScoreData {
    overallScore: number;
    category: 'excellent' | 'good' | 'fair' | 'needs-improvement';
    metrics: {
        savings: number;
        debt: number;
        expenses: number;
        investments: number;
        emergency: number;
    };
    insights: string[];
}

export function FinancialHealthScore() {
    const { userId } = useUser();
    const [data, setData] = useState<HealthScoreData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const seed = userId || 'default-user';

            const prompt = `Generate realistic financial health score data. Return JSON:
            {
                "overallScore": <number 0-100>,
                "category": "excellent" or "good" or "fair" or "needs-improvement",
                "metrics": {
                    "savings": <number 0-100>,
                    "debt": <number 0-100>,
                    "expenses": <number 0-100>,
                    "investments": <number 0-100>,
                    "emergency": <number 0-100>
                },
                "insights": ["<insight 1>", "<insight 2>", "<insight 3>"]
            }`;

            const geminiData = await generateWithGemini(prompt, seed, () => {
                return generateSeededData(seed, (rng) => {
                    const metrics = {
                        savings: rng.nextInt(60, 95),
                        debt: rng.nextInt(70, 100),
                        expenses: rng.nextInt(65, 90),
                        investments: rng.nextInt(50, 85),
                        emergency: rng.nextInt(55, 90),
                    };
                    const overallScore = Math.round(
                        (metrics.savings + metrics.debt + metrics.expenses + metrics.investments + metrics.emergency) / 5
                    );

                    let category: 'excellent' | 'good' | 'fair' | 'needs-improvement';
                    if (overallScore >= 85) category = 'excellent';
                    else if (overallScore >= 70) category = 'good';
                    else if (overallScore >= 55) category = 'fair';
                    else category = 'needs-improvement';

                    return {
                        overallScore,
                        category,
                        metrics,
                        insights: [
                            'Emergency fund covers 3 months of expenses',
                            'Debt-to-income ratio is healthy',
                            'Consider increasing investment allocation',
                        ],
                    };
                });
            });

            setData(geminiData);
            setLoading(false);
        };

        loadData();
    }, [userId]);

    if (loading || !data) {
        return (
            <Card className="border-gray-200 dark:border-gray-800">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Heart className="h-5 w-5" />
                        Financial Health
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-32 flex items-center justify-center">
                        <div className="animate-pulse text-gray-400">Loading...</div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    const getScoreColor = (score: number) => {
        if (score >= 85) return 'text-green-600 dark:text-green-400';
        if (score >= 70) return 'text-blue-600 dark:text-blue-400';
        if (score >= 55) return 'text-yellow-600 dark:text-yellow-400';
        return 'text-red-600 dark:text-red-400';
    };

    const getCategoryBadge = (category: string) => {
        const variants = {
            excellent: { variant: 'default' as const, icon: CheckCircle2 },
            good: { variant: 'default' as const, icon: TrendingUp },
            fair: { variant: 'warning' as const, icon: AlertTriangle },
            'needs-improvement': { variant: 'error' as const, icon: AlertTriangle },
        };
        return variants[category as keyof typeof variants] || variants.fair;
    };

    const badge = getCategoryBadge(data.category);
    const Icon = badge.icon;

    return (
        <Card className="border-gray-200 dark:border-gray-800">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Heart className="h-5 w-5" />
                    Financial Health Score
                </CardTitle>
                <CardDescription>Your overall financial wellness</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="text-center py-4">
                    <div className={`text-5xl font-bold ${getScoreColor(data.overallScore)}`}>
                        {data.overallScore}
                    </div>
                    <Badge variant={badge.variant} className="mt-2">
                        <Icon className="h-3 w-3 mr-1" />
                        {data.category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Badge>
                </div>

                <div className="space-y-3 pt-4 border-t border-gray-200 dark:border-gray-800">
                    {Object.entries(data.metrics).map(([key, value]) => (
                        <div key={key}>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="capitalize">{key}</span>
                                <span className="font-medium">{value}%</span>
                            </div>
                            <Progress value={value} className="h-2" />
                        </div>
                    ))}
                </div>

                {data.insights.length > 0 && (
                    <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
                        <p className="text-sm font-medium mb-2">Key Insights</p>
                        <ul className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                            {data.insights.map((insight, i) => (
                                <li key={i} className="flex items-start gap-2">
                                    <CheckCircle2 className="h-3 w-3 mt-0.5 text-green-600 dark:text-green-400 flex-shrink-0" />
                                    <span>{insight}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

