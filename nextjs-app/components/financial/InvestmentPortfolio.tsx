'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import { useUser } from '@/contexts/UserContext';
import { generateWithGemini, generateSeededData } from '@/lib/geminiDataGenerator';

interface Investment {
    name: string;
    type: string;
    value: number;
    change: number;
    changePercent: number;
}

export function InvestmentPortfolio() {
    const { userId } = useUser();
    const [investments, setInvestments] = useState<Investment[]>([]);
    const [totalValue, setTotalValue] = useState(0);
    const [totalChange, setTotalChange] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const seed = userId || 'default-user';

            const prompt = `Generate realistic investment portfolio. Return JSON:
            {
                "investments": [
                    {
                        "name": "<investment name>",
                        "type": "<type like Stocks, Mutual Funds, Bonds, etc>",
                        "value": <current value>,
                        "change": <change amount positive or negative>,
                        "changePercent": <change percentage>
                    },
                    ...
                ]
            }
            Include 4-5 different investments.`;

            const geminiData = await generateWithGemini(prompt, seed, () => {
                return generateSeededData(seed, (rng) => {
                    const types = [
                        { name: 'Equity Mutual Fund', type: 'Mutual Funds' },
                        { name: 'Tech Stocks', type: 'Stocks' },
                        { name: 'Government Bonds', type: 'Bonds' },
                        { name: 'Gold ETF', type: 'ETF' },
                        { name: 'Real Estate Fund', type: 'REIT' },
                    ];

                    const investments = types.map((item) => {
                        const value = rng.nextInt(100000, 500000);
                        const changePercent = rng.nextFloat(-5, 8);
                        const change = (value * changePercent) / 100;

                        return {
                            name: item.name,
                            type: item.type,
                            value,
                            change,
                            changePercent,
                        };
                    });

                    const total = investments.reduce((sum, inv) => sum + inv.value, 0);
                    const totalChangeAmount = investments.reduce((sum, inv) => sum + inv.change, 0);

                    return {
                        investments,
                        totalValue: total,
                        totalChange: totalChangeAmount,
                    };
                });
            });

            setInvestments(geminiData.investments || []);
            setTotalValue(geminiData.totalValue || 0);
            setTotalChange(geminiData.totalChange || 0);
            setLoading(false);
        };

        loadData();
    }, [userId]);

    if (loading || investments.length === 0) {
        return (
            <Card className="border-gray-200 dark:border-gray-800">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="h-5 w-5" />
                        Investment Portfolio
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

    const totalChangePercent = totalValue > 0 ? (totalChange / (totalValue - totalChange)) * 100 : 0;

    return (
        <Card className="border-gray-200 dark:border-gray-800">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Investment Portfolio
                </CardTitle>
                <CardDescription>Your investment holdings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="pb-4 border-b border-gray-200 dark:border-gray-800">
                    <div className="text-3xl font-bold">
                        ₹{totalValue.toLocaleString('en-IN')}
                    </div>
                    <div className={`flex items-center gap-1 text-sm mt-1 ${totalChange >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                        }`}>
                        {totalChange >= 0 ? (
                            <TrendingUp className="h-4 w-4" />
                        ) : (
                            <TrendingDown className="h-4 w-4" />
                        )}
                        <span>
                            ₹{Math.abs(totalChange).toLocaleString('en-IN')} ({totalChangePercent >= 0 ? '+' : ''}{totalChangePercent.toFixed(2)}%)
                        </span>
                    </div>
                </div>

                <div className="space-y-3">
                    {investments.map((investment, index) => (
                        <div key={index} className="flex items-center justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <span className="font-medium text-sm">{investment.name}</span>
                                    <Badge variant="outline" className="text-xs">
                                        {investment.type}
                                    </Badge>
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                    ₹{investment.value.toLocaleString('en-IN')}
                                </div>
                            </div>
                            <div className={`text-right ${investment.change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                                }`}>
                                <div className="flex items-center gap-1 text-sm font-medium">
                                    {investment.change >= 0 ? (
                                        <TrendingUp className="h-3 w-3" />
                                    ) : (
                                        <TrendingDown className="h-3 w-3" />
                                    )}
                                    <span>
                                        {investment.changePercent >= 0 ? '+' : ''}{investment.changePercent.toFixed(2)}%
                                    </span>
                                </div>
                                <div className="text-xs">
                                    {investment.change >= 0 ? '+' : ''}₹{Math.abs(investment.change).toLocaleString('en-IN')}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

