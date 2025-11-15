'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { CreditCard, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useUser } from '@/contexts/UserContext';
import { generateWithGemini, generateSeededData } from '@/lib/geminiDataGenerator';

interface CreditScoreData {
    score: number;
    rating: 'excellent' | 'good' | 'fair' | 'poor';
    factors: {
        paymentHistory: number;
        creditUtilization: number;
        creditAge: number;
        creditMix: number;
        inquiries: number;
    };
    recommendations: string[];
}

export function CreditScoreCard() {
    const { userId } = useUser();
    const [data, setData] = useState<CreditScoreData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const seed = userId || 'default-user';

            const prompt = `Generate realistic credit score data. Return JSON:
            {
                "score": <number between 300-850>,
                "rating": "excellent" or "good" or "fair" or "poor",
                "factors": {
                    "paymentHistory": <number 0-100>,
                    "creditUtilization": <number 0-100>,
                    "creditAge": <number 0-100>,
                    "creditMix": <number 0-100>,
                    "inquiries": <number 0-100>
                },
                "recommendations": ["<recommendation 1>", "<recommendation 2>"]
            }`;

            const geminiData = await generateWithGemini(prompt, seed, () => {
                return generateSeededData(seed, (rng) => {
                    const score = rng.nextInt(300, 850);
                    let rating: 'excellent' | 'good' | 'fair' | 'poor';
                    if (score >= 750) rating = 'excellent';
                    else if (score >= 700) rating = 'good';
                    else if (score >= 650) rating = 'fair';
                    else rating = 'poor';

                    return {
                        score,
                        rating,
                        factors: {
                            paymentHistory: rng.nextInt(70, 100),
                            creditUtilization: rng.nextInt(60, 95),
                            creditAge: rng.nextInt(50, 100),
                            creditMix: rng.nextInt(40, 90),
                            inquiries: rng.nextInt(80, 100),
                        },
                        recommendations: [
                            'Pay bills on time consistently',
                            'Keep credit utilization below 30%',
                            'Avoid opening too many new accounts',
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
                        <CreditCard className="h-5 w-5" />
                        Credit Score
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
        if (score >= 750) return 'text-green-600 dark:text-green-400';
        if (score >= 700) return 'text-blue-600 dark:text-blue-400';
        if (score >= 650) return 'text-yellow-600 dark:text-yellow-400';
        return 'text-red-600 dark:text-red-400';
    };

    const getRatingBadge = (rating: string) => {
        const variants = {
            excellent: { variant: 'default' as const, icon: CheckCircle2 },
            good: { variant: 'default' as const, icon: TrendingUp },
            fair: { variant: 'warning' as const, icon: AlertCircle },
            poor: { variant: 'error' as const, icon: AlertCircle },
        };
        return variants[rating as keyof typeof variants] || variants.fair;
    };

    const badge = getRatingBadge(data.rating);
    const Icon = badge.icon;

    return (
        <Card className="border-gray-200 dark:border-gray-800">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <CreditCard className="h-5 w-5" />
                    Credit Score
                </CardTitle>
                <CardDescription>Your current credit health</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="text-center py-4">
                    <div className={`text-5xl font-bold ${getScoreColor(data.score)}`}>
                        {data.score}
                    </div>
                    <Badge variant={badge.variant} className="mt-2">
                        <Icon className="h-3 w-3 mr-1" />
                        {data.rating.charAt(0).toUpperCase() + data.rating.slice(1)}
                    </Badge>
                </div>

                <div className="space-y-3 pt-4 border-t border-gray-200 dark:border-gray-800">
                    <div>
                        <div className="flex justify-between text-sm mb-1">
                            <span>Payment History</span>
                            <span className="font-medium">{data.factors.paymentHistory}%</span>
                        </div>
                        <Progress value={data.factors.paymentHistory} className="h-2" />
                    </div>
                    <div>
                        <div className="flex justify-between text-sm mb-1">
                            <span>Credit Utilization</span>
                            <span className="font-medium">{data.factors.creditUtilization}%</span>
                        </div>
                        <Progress value={data.factors.creditUtilization} className="h-2" />
                    </div>
                    <div>
                        <div className="flex justify-between text-sm mb-1">
                            <span>Credit Age</span>
                            <span className="font-medium">{data.factors.creditAge}%</span>
                        </div>
                        <Progress value={data.factors.creditAge} className="h-2" />
                    </div>
                </div>

                {data.recommendations.length > 0 && (
                    <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
                        <p className="text-sm font-medium mb-2">Recommendations</p>
                        <ul className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                            {data.recommendations.map((rec, i) => (
                                <li key={i} className="flex items-start gap-2">
                                    <span className="mt-0.5">•</span>
                                    <span>{rec}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

