'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { subscriptionsAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { CreditCard, TrendingDown, DollarSign, Calendar, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function SubscriptionsPage() {
    const [userId] = useState('user_123'); // TODO: Get from auth context
    const [subscriptions, setSubscriptions] = useState<any[]>([]);
    const [unused, setUnused] = useState<any[]>([]);
    const [savings, setSavings] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [subsData, unusedData, savingsData] = await Promise.all([
                subscriptionsAPI.getSubscriptions(userId).catch(() => ({ subscriptions: [] })),
                subscriptionsAPI.getUnusedSubscriptions(userId).catch(() => ({ unused_subscriptions: [] })),
                subscriptionsAPI.getSavings(userId).catch(() => null),
            ]);
            setSubscriptions(subsData.subscriptions || []);
            setUnused(unusedData.unused_subscriptions || []);
            setSavings(savingsData);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load subscriptions',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        return status === 'active' ? 'success' : 'warning';
    };

    return (
        <Container>
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl md:text-4xl font-bold text-black dark:text-white">Subscriptions</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        Track and optimize your subscriptions
                    </p>
                </div>

                {subscriptions.length > 0 && subscriptions[0]?.summary && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Total Subscriptions
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{subscriptions[0].summary.total_subscriptions}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Active
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{subscriptions[0].summary.active}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Monthly Cost
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">${subscriptions[0].summary.monthly_cost?.toFixed(2)}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Annual Cost
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">${subscriptions[0].summary.annual_cost?.toFixed(2)}</div>
                            </CardContent>
                        </Card>
                    </div>
                )}

                <Tabs defaultValue="all">
                    <TabsList>
                        <TabsTrigger value="all">All Subscriptions</TabsTrigger>
                        <TabsTrigger value="unused">Unused</TabsTrigger>
                        <TabsTrigger value="savings">Savings</TabsTrigger>
                    </TabsList>

                    <TabsContent value="all" className="space-y-4">
                        {loading ? (
                            <div className="space-y-4">
                                {[1, 2, 3].map((i) => (
                                    <Skeleton key={i} className="h-32" />
                                ))}
                            </div>
                        ) : subscriptions.length > 0 ? (
                            subscriptions.map((sub) => (
                                <Card key={sub.subscription_id}>
                                    <CardHeader>
                                        <div className="flex items-center justify-between">
                                            <CardTitle className="text-lg">{sub.name}</CardTitle>
                                            <Badge variant={getStatusColor(sub.status) as any}>{sub.status}</Badge>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                            <div>
                                                <p className="text-gray-600 dark:text-gray-400">Amount</p>
                                                <p className="font-medium">${sub.amount?.toFixed(2)}/{sub.frequency}</p>
                                            </div>
                                            <div>
                                                <p className="text-gray-600 dark:text-gray-400">Billing Day</p>
                                                <p className="font-medium">{sub.billing_day}</p>
                                            </div>
                                            <div>
                                                <p className="text-gray-600 dark:text-gray-400">Total Spent</p>
                                                <p className="font-medium">${sub.total_spent?.toFixed(2)}</p>
                                            </div>
                                            <div>
                                                <p className="text-gray-600 dark:text-gray-400">Usage</p>
                                                <p className="font-medium capitalize">{sub.usage_estimate || 'N/A'}</p>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))
                        ) : (
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center py-8">
                                        <CreditCard className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600 mb-4" />
                                        <p className="text-sm text-gray-600 dark:text-gray-400">No subscriptions detected</p>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </TabsContent>

                    <TabsContent value="unused" className="space-y-4">
                        {loading ? (
                            <Skeleton className="h-64" />
                        ) : unused.length > 0 ? (
                            <>
                                {unused.map((sub) => (
                                    <Card key={sub.subscription_id}>
                                        <CardHeader>
                                            <div className="flex items-center justify-between">
                                                <CardTitle className="text-lg">{sub.name}</CardTitle>
                                                <Badge variant="warning">Unused</Badge>
                                            </div>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="space-y-4">
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                    <div>
                                                        <p className="text-gray-600 dark:text-gray-400">Amount</p>
                                                        <p className="font-medium">${sub.amount?.toFixed(2)}/month</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-gray-600 dark:text-gray-400">Months Unused</p>
                                                        <p className="font-medium">{sub.months_unused}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-gray-600 dark:text-gray-400">Potential Savings</p>
                                                        <p className="font-medium text-green-600 dark:text-green-400">
                                                            ${sub.potential_savings_annual?.toFixed(2)}/year
                                                        </p>
                                                    </div>
                                                </div>
                                                {sub.recommendation && (
                                                    <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                                        <p className="text-sm font-medium mb-1">Recommendation</p>
                                                        <p className="text-sm text-gray-700 dark:text-gray-300">{sub.recommendation}</p>
                                                    </div>
                                                )}
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                                {unused[0]?.total_potential_savings && (
                                    <Card>
                                        <CardContent className="pt-6">
                                            <div className="text-center">
                                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Total Potential Savings</p>
                                                <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                                                    ${unused[0].total_potential_savings.toFixed(2)}/year
                                                </p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}
                            </>
                        ) : (
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center py-8">
                                        <CheckCircle2 className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600 mb-4" />
                                        <p className="text-sm text-gray-600 dark:text-gray-400">No unused subscriptions found</p>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </TabsContent>

                    <TabsContent value="savings" className="space-y-4">
                        {loading ? (
                            <Skeleton className="h-64" />
                        ) : savings ? (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Savings Opportunities</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Potential Annual Savings</p>
                                            <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                                                ${savings.potential_savings?.toFixed(2) || '0.00'}
                                            </p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ) : (
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center py-8">
                                        <TrendingDown className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600 mb-4" />
                                        <p className="text-sm text-gray-600 dark:text-gray-400">No savings data available</p>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </TabsContent>
                </Tabs>
            </div>
        </Container>
    );
}

