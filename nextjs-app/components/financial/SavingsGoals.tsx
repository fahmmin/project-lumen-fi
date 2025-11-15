'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Target, TrendingUp, CheckCircle2 } from 'lucide-react';
import { useUser } from '@/contexts/UserContext';
import { generateWithGemini, generateSeededData } from '@/lib/geminiDataGenerator';

interface Goal {
    name: string;
    target: number;
    current: number;
    deadline: string;
    status: 'on-track' | 'behind' | 'completed';
}

export function SavingsGoals() {
    const { userId } = useUser();
    const [goals, setGoals] = useState<Goal[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const seed = userId || 'default-user';

            const prompt = `Generate realistic savings goals. Return JSON array:
            [
                {
                    "name": "<goal name>",
                    "target": <target amount>,
                    "current": <current amount>,
                    "deadline": "<YYYY-MM-DD>",
                    "status": "on-track" or "behind" or "completed"
                },
                ...
            ]
            Include 3-4 goals like Emergency Fund, Vacation, Car, House Down Payment, etc.`;

            const geminiData = await generateWithGemini(prompt, seed, () => {
                return generateSeededData(seed, (rng) => {
                    const goalTypes = [
                        { name: 'Emergency Fund', target: 500000, months: 12 },
                        { name: 'Vacation', target: 200000, months: 6 },
                        { name: 'Car Down Payment', target: 300000, months: 18 },
                        { name: 'House Down Payment', target: 2000000, months: 36 },
                    ];

                    return goalTypes.map((type, i) => {
                        const progress = rng.nextFloat(0.2, 0.9);
                        const current = Math.round(type.target * progress);
                        const deadline = new Date();
                        deadline.setMonth(deadline.getMonth() + type.months);

                        let status: 'on-track' | 'behind' | 'completed';
                        const monthsElapsed = type.months * (1 - progress);
                        const expectedProgress = 1 - (monthsElapsed / type.months);
                        if (progress >= 1) status = 'completed';
                        else if (progress >= expectedProgress * 0.9) status = 'on-track';
                        else status = 'behind';

                        return {
                            name: type.name,
                            target: type.target,
                            current,
                            deadline: deadline.toISOString().split('T')[0],
                            status,
                        };
                    });
                });
            });

            setGoals(Array.isArray(geminiData) ? geminiData : []);
            setLoading(false);
        };

        loadData();
    }, [userId]);

    if (loading || goals.length === 0) {
        return (
            <Card className="border-gray-200 dark:border-gray-800">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5" />
                        Savings Goals
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

    return (
        <Card className="border-gray-200 dark:border-gray-800">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Savings Goals
                </CardTitle>
                <CardDescription>Track your financial objectives</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {goals.map((goal, index) => {
                    const progress = Math.min((goal.current / goal.target) * 100, 100);
                    const remaining = goal.target - goal.current;
                    const deadlineDate = new Date(goal.deadline);
                    const daysRemaining = Math.ceil((deadlineDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));

                    const statusBadge = {
                        'on-track': { variant: 'default' as const, label: 'On Track' },
                        'behind': { variant: 'warning' as const, label: 'Behind' },
                        'completed': { variant: 'default' as const, label: 'Completed' },
                    }[goal.status];

                    return (
                        <div key={index} className="space-y-2 pb-4 border-b border-gray-200 dark:border-gray-800 last:border-0 last:pb-0">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <h4 className="font-medium">{goal.name}</h4>
                                    {goal.status === 'completed' && (
                                        <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                                    )}
                                </div>
                                <Badge variant={statusBadge.variant}>{statusBadge.label}</Badge>
                            </div>

                            <div className="space-y-1">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600 dark:text-gray-400">
                                        ₹{goal.current.toLocaleString('en-IN')} / ₹{goal.target.toLocaleString('en-IN')}
                                    </span>
                                    <span className="font-semibold">{Math.round(progress)}%</span>
                                </div>
                                <Progress value={progress} className="h-2" />
                            </div>

                            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                                <span>Remaining: ₹{remaining.toLocaleString('en-IN')}</span>
                                <span>{daysRemaining > 0 ? `${daysRemaining} days left` : 'Overdue'}</span>
                            </div>
                        </div>
                    );
                })}
            </CardContent>
        </Card>
    );
}

