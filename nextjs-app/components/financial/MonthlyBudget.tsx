'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Wallet, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { useUser } from '@/contexts/UserContext';
import { generateWithGemini, generateSeededData } from '@/lib/geminiDataGenerator';

interface BudgetCategory {
    category: string;
    budgeted: number;
    spent: number;
    remaining: number;
}

export function MonthlyBudget() {
    const { userId } = useUser();
    const [categories, setCategories] = useState<BudgetCategory[]>([]);
    const [totalBudget, setTotalBudget] = useState(0);
    const [totalSpent, setTotalSpent] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const seed = userId || 'default-user';

            const prompt = `Generate realistic monthly budget data. Return JSON:
            {
                "categories": [
                    {
                        "category": "<category name>",
                        "budgeted": <budgeted amount>,
                        "spent": <spent amount>,
                        "remaining": <remaining amount>
                    },
                    ...
                ],
                "totalBudget": <total>,
                "totalSpent": <total>
            }
            Include 5-6 categories.`;

            const geminiData = await generateWithGemini(prompt, seed, () => {
                return generateSeededData(seed, (rng) => {
                    const categoryTypes = [
                        { name: 'Food & Dining', budget: 15000 },
                        { name: 'Transportation', budget: 8000 },
                        { name: 'Shopping', budget: 12000 },
                        { name: 'Entertainment', budget: 6000 },
                        { name: 'Bills & Utilities', budget: 10000 },
                        { name: 'Healthcare', budget: 5000 },
                    ];

                    const categories = categoryTypes.map((cat) => {
                        const spentRatio = rng.nextFloat(0.5, 1.1);
                        const spent = Math.round(cat.budget * spentRatio);
                        const remaining = Math.max(0, cat.budget - spent);

                        return {
                            category: cat.name,
                            budgeted: cat.budget,
                            spent,
                            remaining,
                        };
                    });

                    const totalBudget = categories.reduce((sum, cat) => sum + cat.budgeted, 0);
                    const totalSpent = categories.reduce((sum, cat) => sum + cat.spent, 0);

                    return {
                        categories,
                        totalBudget,
                        totalSpent,
                    };
                });
            });

            setCategories(geminiData.categories || []);
            setTotalBudget(geminiData.totalBudget || 0);
            setTotalSpent(geminiData.totalSpent || 0);
            setLoading(false);
        };

        loadData();
    }, [userId]);

    if (loading || categories.length === 0) {
        return (
            <Card className="border-gray-200 dark:border-gray-800">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Wallet className="h-5 w-5" />
                        Monthly Budget
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

    const totalRemaining = totalBudget - totalSpent;
    const budgetUsage = (totalSpent / totalBudget) * 100;
    const isOverBudget = totalSpent > totalBudget;

    return (
        <Card className="border-gray-200 dark:border-gray-800">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Wallet className="h-5 w-5" />
                    Monthly Budget
                </CardTitle>
                <CardDescription>Budget vs actual spending</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="pb-4 border-b border-gray-200 dark:border-gray-800">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Total Budget</span>
                        <span className="text-lg font-semibold">₹{totalBudget.toLocaleString('en-IN')}</span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Spent</span>
                        <span className={`text-lg font-semibold ${isOverBudget ? 'text-red-600 dark:text-red-400' : ''}`}>
                            ₹{totalSpent.toLocaleString('en-IN')}
                        </span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Remaining</span>
                        <span className={`text-lg font-semibold ${totalRemaining < 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                            ₹{Math.abs(totalRemaining).toLocaleString('en-IN')}
                        </span>
                    </div>
                    <Progress
                        value={Math.min(budgetUsage, 100)}
                        className={`h-3 mt-3 ${isOverBudget ? 'bg-red-100 dark:bg-red-900' : ''}`}
                    />
                    {isOverBudget && (
                        <Badge variant="error" className="mt-2">
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            Over Budget
                        </Badge>
                    )}
                </div>

                <div className="space-y-3">
                    {categories.map((category, index) => {
                        const usage = (category.spent / category.budgeted) * 100;
                        const isOver = category.spent > category.budgeted;

                        return (
                            <div key={index} className="space-y-1">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="font-medium">{category.category}</span>
                                    <div className="flex items-center gap-2">
                                        {isOver ? (
                                            <AlertTriangle className="h-3 w-3 text-red-600 dark:text-red-400" />
                                        ) : usage > 80 ? (
                                            <AlertTriangle className="h-3 w-3 text-yellow-600 dark:text-yellow-400" />
                                        ) : (
                                            <CheckCircle2 className="h-3 w-3 text-green-600 dark:text-green-400" />
                                        )}
                                        <span className={isOver ? 'text-red-600 dark:text-red-400' : ''}>
                                            ₹{category.spent.toLocaleString('en-IN')} / ₹{category.budgeted.toLocaleString('en-IN')}
                                        </span>
                                    </div>
                                </div>
                                <Progress
                                    value={Math.min(usage, 100)}
                                    className={`h-2 ${isOver ? 'bg-red-100 dark:bg-red-900' : ''}`}
                                />
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}

