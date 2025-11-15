'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { ShoppingBag, Home, Car, Utensils, Gamepad2, Heart, GraduationCap } from 'lucide-react';
import { useUser } from '@/contexts/UserContext';
import { generateWithGemini, generateSeededData } from '@/lib/geminiDataGenerator';

interface CategoryData {
    name: string;
    amount: number;
    percentage: number;
    icon: string;
}

const categoryIcons: Record<string, any> = {
    'Food & Dining': Utensils,
    'Shopping': ShoppingBag,
    'Transportation': Car,
    'Entertainment': Gamepad2,
    'Healthcare': Heart,
    'Education': GraduationCap,
    'Housing': Home,
};

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4'];

export function ExpenseCategories() {
    const { userId } = useUser();
    const [data, setData] = useState<CategoryData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const seed = userId || 'default-user';

            const prompt = `Generate realistic expense category breakdown. Return JSON array:
            [
                {"name": "<category>", "amount": <number>, "percentage": <number>},
                ...
            ]
            Include 5-7 categories like Food, Shopping, Transportation, Entertainment, Healthcare, etc.`;

            const geminiData = await generateWithGemini(prompt, seed, () => {
                return generateSeededData(seed, (rng) => {
                    const categories = [
                        { name: 'Food & Dining', base: 0.25 },
                        { name: 'Shopping', base: 0.20 },
                        { name: 'Transportation', base: 0.15 },
                        { name: 'Entertainment', base: 0.12 },
                        { name: 'Healthcare', base: 0.10 },
                        { name: 'Education', base: 0.10 },
                        { name: 'Housing', base: 0.08 },
                    ];

                    const total = rng.nextInt(50000, 200000);
                    return categories.map((cat, i) => {
                        const variance = rng.nextFloat(0.8, 1.2);
                        const percentage = cat.base * variance;
                        return {
                            name: cat.name,
                            amount: Math.round(total * percentage),
                            percentage: Math.round(percentage * 100),
                            icon: cat.name,
                        };
                    }).sort((a, b) => b.amount - a.amount);
                });
            });

            setData(Array.isArray(geminiData) ? geminiData : []);
            setLoading(false);
        };

        loadData();
    }, [userId]);

    if (loading || data.length === 0) {
        return (
            <Card className="border-gray-200 dark:border-gray-800">
                <CardHeader>
                    <CardTitle>Expense Categories</CardTitle>
                    <CardDescription>Monthly spending breakdown</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="h-64 flex items-center justify-center">
                        <div className="animate-pulse text-gray-400">Loading...</div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    const total = data.reduce((sum, item) => sum + item.amount, 0);

    return (
        <Card className="border-gray-200 dark:border-gray-800">
            <CardHeader>
                <CardTitle>Expense Categories</CardTitle>
                <CardDescription>Monthly spending breakdown</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-64 mb-4">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percentage }) => `${name}: ${percentage}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="amount"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value: number) => `₹${value.toLocaleString('en-IN')}`}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                <div className="space-y-2 pt-4 border-t border-gray-200 dark:border-gray-800">
                    {data.map((item, index) => {
                        const Icon = categoryIcons[item.icon] || ShoppingBag;
                        return (
                            <div key={item.name} className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Icon className="h-4 w-4 text-gray-400" />
                                    <span className="text-sm">{item.name}</span>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm font-semibold">
                                        ₹{item.amount.toLocaleString('en-IN')}
                                    </div>
                                    <div className="text-xs text-gray-500">{item.percentage}%</div>
                                </div>
                            </div>
                        );
                    })}
                    <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-800 font-semibold">
                        <span>Total</span>
                        <span>₹{total.toLocaleString('en-IN')}</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

