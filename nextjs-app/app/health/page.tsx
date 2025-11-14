'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { financeAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { Heart, TrendingUp, TrendingDown, AlertCircle, Brain, Activity, Wallet } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

export default function HealthPage() {
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [healthScore, setHealthScore] = useState<any>(null);
    const [behavior, setBehavior] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        if (userId) {
            loadData();
        }
    }, [userId]);

    const loadData = async () => {
        if (!userId) return;
        try {
            setLoading(true);
            const [health, behaviorData] = await Promise.all([
                financeAPI.getHealthScore(userId).catch(() => null),
                financeAPI.getBehavior(userId).catch(() => null),
            ]);
            setHealthScore(health);
            setBehavior(behaviorData);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load health data',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-600 dark:text-green-400';
        if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
        return 'text-red-600 dark:text-red-400';
    };

    const getRatingColor = (rating: string) => {
        switch (rating.toLowerCase()) {
            case 'excellent':
            case 'good':
                return 'success';
            case 'fair':
            case 'moderate':
                return 'warning';
            default:
                return 'error';
        }
    };

    return (
        <Container>
            <div className="space-y-6">
                {!isConnected && (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <Wallet className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                            <p className="text-gray-600 dark:text-gray-400 mb-4">
                                Connect your wallet to view health score
                            </p>
                            <Button onClick={connectWallet}>
                                <Wallet className="h-4 w-4 mr-2" />
                                Connect Wallet
                            </Button>
                        </CardContent>
                    </Card>
                )}
                {userLoading || (loading && isConnected) ? (
                    <Skeleton className="h-64 w-full" />
                ) : !isConnected ? null : (
                    <>
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold text-black dark:text-white">Financial Health</h1>
                            <p className="text-gray-600 dark:text-gray-400 mt-2">
                                Track your financial health score and behavior patterns
                            </p>
                        </div>

                        <Tabs defaultValue="score">
                            <TabsList>
                                <TabsTrigger value="score">Health Score</TabsTrigger>
                                <TabsTrigger value="behavior">Behavior Analysis</TabsTrigger>
                            </TabsList>

                            <TabsContent value="score" className="space-y-6">
                                {loading ? (
                                    <Skeleton className="h-64" />
                                ) : healthScore ? (
                                    <>
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>Overall Health Score</CardTitle>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="space-y-6">
                                                    <div className="text-center">
                                                        <div className={`text-6xl font-bold ${getScoreColor(healthScore.health_score)}`}>
                                                            {healthScore.health_score}
                                                        </div>
                                                        <p className="text-lg text-gray-600 dark:text-gray-400 mt-2">
                                                            {healthScore.rating}
                                                        </p>
                                                        <Progress value={healthScore.health_score} className="mt-4 h-3" />
                                                    </div>

                                                    {healthScore.breakdown && (
                                                        <div className="space-y-4">
                                                            <h3 className="font-semibold">Score Breakdown</h3>
                                                            {Object.entries(healthScore.breakdown).map(([key, data]: [string, any]) => (
                                                                <div key={key} className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                                                    <div className="flex items-center justify-between mb-2">
                                                                        <div>
                                                                            <p className="font-medium capitalize">{key.replace('_', ' ')}</p>
                                                                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                                                                {data.description}
                                                                            </p>
                                                                        </div>
                                                                        <div className="text-right">
                                                                            <p className="text-2xl font-bold">{data.score}/{data.max}</p>
                                                                            <Badge variant={getRatingColor(data.rating) as any}>
                                                                                {data.rating}
                                                                            </Badge>
                                                                        </div>
                                                                    </div>
                                                                    <Progress value={(data.score / data.max) * 100} className="h-2" />
                                                                </div>
                                                            ))}
                                                        </div>
                                                    )}

                                                    {healthScore.recommendations && healthScore.recommendations.length > 0 && (
                                                        <div>
                                                            <h3 className="font-semibold mb-4">Recommendations</h3>
                                                            <div className="space-y-2">
                                                                {healthScore.recommendations.map((rec: string, index: number) => (
                                                                    <div
                                                                        key={index}
                                                                        className="flex items-start gap-3 p-3 border border-gray-200 dark:border-gray-800 rounded-lg"
                                                                    >
                                                                        <AlertCircle className="h-5 w-5 text-gray-600 dark:text-gray-400 mt-0.5" />
                                                                        <p className="text-sm text-gray-700 dark:text-gray-300">{rec}</p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    </>
                                ) : (
                                    <Card>
                                        <CardContent className="pt-6">
                                            <div className="text-center py-8">
                                                <Heart className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600 mb-4" />
                                                <p className="text-sm text-gray-600 dark:text-gray-400">No health score data available</p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}
                            </TabsContent>

                            <TabsContent value="behavior" className="space-y-6">
                                {loading ? (
                                    <Skeleton className="h-64" />
                                ) : behavior ? (
                                    <>
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>Behavior Analysis</CardTitle>
                                                <CardDescription>
                                                    Impulse Score: {(behavior.impulse_score * 100).toFixed(0)}%
                                                </CardDescription>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="space-y-4">
                                                    {behavior.patterns && behavior.patterns.map((pattern: any, index: number) => (
                                                        <Card key={index}>
                                                            <CardHeader>
                                                                <div className="flex items-center justify-between">
                                                                    <CardTitle className="text-lg capitalize">{pattern.type.replace('_', ' ')}</CardTitle>
                                                                    <Badge
                                                                        variant={
                                                                            pattern.severity === 'low'
                                                                                ? 'default'
                                                                                : pattern.severity === 'medium'
                                                                                    ? 'warning'
                                                                                    : 'error'
                                                                        }
                                                                    >
                                                                        {pattern.severity}
                                                                    </Badge>
                                                                </div>
                                                            </CardHeader>
                                                            <CardContent>
                                                                <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">{pattern.finding}</p>
                                                                {pattern.data && (
                                                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                                                        {Object.entries(pattern.data).map(([key, value]: [string, any]) => (
                                                                            <div key={key}>
                                                                                <p className="text-gray-600 dark:text-gray-400 capitalize">
                                                                                    {key.replace('_', ' ')}
                                                                                </p>
                                                                                <p className="font-medium">
                                                                                    {typeof value === 'number' ? `$${value.toFixed(2)}` : value}
                                                                                </p>
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                )}
                                                            </CardContent>
                                                        </Card>
                                                    ))}
                                                </div>
                                            </CardContent>
                                        </Card>

                                        {behavior.recommendations && behavior.recommendations.length > 0 && (
                                            <Card>
                                                <CardHeader>
                                                    <CardTitle>Recommendations</CardTitle>
                                                </CardHeader>
                                                <CardContent>
                                                    <div className="space-y-2">
                                                        {behavior.recommendations.map((rec: string, index: number) => (
                                                            <div
                                                                key={index}
                                                                className="flex items-start gap-3 p-3 border border-gray-200 dark:border-gray-800 rounded-lg"
                                                            >
                                                                <Brain className="h-5 w-5 text-gray-600 dark:text-gray-400 mt-0.5" />
                                                                <p className="text-sm text-gray-700 dark:text-gray-300">{rec}</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        )}
                                    </>
                                ) : (
                                    <Card>
                                        <CardContent className="pt-6">
                                            <div className="text-center py-8">
                                                <Activity className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600 mb-4" />
                                                <p className="text-sm text-gray-600 dark:text-gray-400">No behavior data available</p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}
                            </TabsContent>
                        </Tabs>
                    </>
                )}
            </div>
        </Container>
    );
}

