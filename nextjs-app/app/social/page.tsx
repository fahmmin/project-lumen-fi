'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { socialAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { TrendingUp, Users, BarChart3, Target, ArrowUp, ArrowDown, Wallet } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

export default function SocialPage() {
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [percentile, setPercentile] = useState<any>(null);
    const [insights, setInsights] = useState<any>(null);
    const [category, setCategory] = useState<string>('groceries');
    const [leaderboard, setLeaderboard] = useState<any>(null);
    const [period, setPeriod] = useState<string>('month');
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    const loadPercentile = async () => {
        if (!userId) return;
        setLoading(true);
        try {
            const data = await socialAPI.getUserPercentile(userId, period);
            setPercentile(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load percentile data',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const loadInsights = async () => {
        if (!userId) return;
        try {
            const data = await socialAPI.getSocialInsights(userId, period);
            setInsights(data);
        } catch (error: any) {
            console.error('Failed to load insights:', error);
        }
    };

    const loadCategoryLeaderboard = async () => {
        try {
            const data = await socialAPI.getCategoryLeaderboard(category, period, 10);
            setLeaderboard(data);
        } catch (error: any) {
            console.error('Failed to load leaderboard:', error);
        }
    };

    useEffect(() => {
        loadPercentile();
        loadInsights();
    }, [userId, period]);

    useEffect(() => {
        loadCategoryLeaderboard();
    }, [category, period]);

    const getPercentileColor = (p: number) => {
        if (p >= 75) return 'text-red-600 dark:text-red-400';
        if (p >= 50) return 'text-yellow-600 dark:text-yellow-400';
        return 'text-green-600 dark:text-green-400';
    };

    const getPercentileStatus = (p: number) => {
        if (p >= 75) return 'High Spender';
        if (p >= 50) return 'Average';
        return 'Low Spender';
    };

    return (
        <Container>
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold mb-2">Social Comparison</h1>
                    <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                        See how your spending compares to others (anonymized)
                    </p>
                </div>

                {/* Period Selector */}
                {isConnected && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Time Period</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <select
                                value={period}
                                onChange={(e) => setPeriod(e.target.value)}
                                className="w-full px-3 py-2 border rounded-lg"
                            >
                                <option value="month">Month</option>
                                <option value="quarter">Quarter</option>
                                <option value="year">Year</option>
                            </select>
                        </CardContent>
                    </Card>
                )}

                {!isConnected && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Connect Wallet</CardTitle>
                            <CardDescription>Connect your wallet to view your social comparison</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button onClick={connectWallet} className="w-full sm:w-auto">
                                <Wallet className="h-4 w-4 mr-2" />
                                Connect Wallet
                            </Button>
                        </CardContent>
                    </Card>
                )}

                {userLoading || loading ? (
                    <Skeleton className="h-64 w-full" />
                ) : percentile ? (
                    <Tabs defaultValue="overview" className="space-y-4">
                        <TabsList>
                            <TabsTrigger value="overview">Overview</TabsTrigger>
                            <TabsTrigger value="categories">Categories</TabsTrigger>
                            <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
                        </TabsList>

                        <TabsContent value="overview" className="space-y-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Your Spending Percentile</CardTitle>
                                    <CardDescription>
                                        {percentile.overall?.percentile !== undefined
                                            ? `You spend more than ${percentile.overall.percentile}% of users`
                                            : 'No data available'}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="text-center">
                                            <div className={`text-4xl sm:text-6xl font-bold mb-2 ${getPercentileColor(percentile.overall?.percentile || 0)}`}>
                                                {percentile.overall?.percentile || 0}%
                                            </div>
                                            <Badge variant="outline" className="text-lg">
                                                {getPercentileStatus(percentile.overall?.percentile || 0)}
                                            </Badge>
                                        </div>
                                        <Progress value={percentile.overall?.percentile || 0} className="h-3" />
                                        <div className="grid grid-cols-2 gap-4 mt-4">
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Your Spending</p>
                                                <p className="text-2xl font-bold">
                                                    ${percentile.overall?.user_spending?.toLocaleString() || '0'}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Average</p>
                                                <p className="text-2xl font-bold">
                                                    ${percentile.overall?.average_spending?.toLocaleString() || '0'}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {insights && insights.insights && (
                                <Card>
                                    <CardHeader>
                                        <CardTitle>Insights</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-2">
                                            {insights.insights.map((insight: string, index: number) => (
                                                <div key={index} className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                                    <p className="text-sm">{insight}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            )}
                        </TabsContent>

                        <TabsContent value="categories" className="space-y-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Category Percentiles</CardTitle>
                                    <CardDescription>How you compare in each spending category</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        {percentile.categories?.map((cat: any, index: number) => (
                                            <div key={index}>
                                                <div className="flex justify-between mb-2">
                                                    <span className="font-semibold capitalize">{cat.category}</span>
                                                    <span className={`font-bold ${getPercentileColor(cat.percentile)}`}>
                                                        {cat.percentile}%
                                                    </span>
                                                </div>
                                                <Progress value={cat.percentile} className="h-2" />
                                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                                    <span>You: ${cat.user_spending?.toLocaleString() || '0'}</span>
                                                    <span>Avg: ${cat.average_spending?.toLocaleString() || '0'}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        <TabsContent value="leaderboard" className="space-y-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Category Leaderboard</CardTitle>
                                    <CardDescription>Top spenders in selected category (anonymized)</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="mb-4">
                                        <Input
                                            placeholder="Category (e.g., groceries, dining)"
                                            value={category}
                                            onChange={(e) => setCategory(e.target.value)}
                                        />
                                    </div>
                                    {leaderboard && (
                                        <div className="space-y-2">
                                            {leaderboard.top_users?.map((user: any, index: number) => (
                                                <div
                                                    key={index}
                                                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
                                                >
                                                    <div className="flex items-center gap-3">
                                                        <div className="w-8 h-8 rounded-full bg-black dark:bg-white text-white dark:text-black flex items-center justify-center font-bold">
                                                            {index + 1}
                                                        </div>
                                                        <span className="font-semibold">{user.display_name || 'Anonymous'}</span>
                                                    </div>
                                                    <span className="font-bold">${user.amount?.toLocaleString() || '0'}</span>
                                                </div>
                                            ))}
                                            {leaderboard.average && (
                                                <div className="mt-4 p-3 border-t border-gray-200 dark:border-gray-800">
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                        Category Average: <strong>${leaderboard.average.toLocaleString()}</strong>
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </TabsContent>
                    </Tabs>
                ) : !isConnected ? (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <Wallet className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                            <p className="text-gray-600 dark:text-gray-400">
                                Connect your wallet to view your social comparison
                            </p>
                        </CardContent>
                    </Card>
                ) : !userId ? (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <p className="text-gray-600 dark:text-gray-400">
                                Loading user information...
                            </p>
                        </CardContent>
                    </Card>
                ) : null}
            </div>
        </Container>
    );
}

