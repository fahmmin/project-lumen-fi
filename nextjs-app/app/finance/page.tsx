'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { financeAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { DollarSign, TrendingUp, TrendingDown, Target, AlertCircle, CheckCircle2 } from 'lucide-react';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

const COLORS = ['#000000', '#666666', '#999999', '#CCCCCC', '#E5E5E5'];

export default function FinancePage() {
    const [userId] = useState('user_123'); // TODO: Get from auth context
    const [dashboard, setDashboard] = useState<any>(null);
    const [spending, setSpending] = useState<any>(null);
    const [predictions, setPredictions] = useState<any>(null);
    const [insights, setInsights] = useState<any>(null);
    const [budgetRecs, setBudgetRecs] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('dashboard');
    const [period, setPeriod] = useState<'month' | 'quarter' | 'year'>('month');
    const { toast } = useToast();

    useEffect(() => {
        loadDashboard();
    }, [period]);

    const loadDashboard = async () => {
        try {
            setLoading(true);
            const data = await financeAPI.getDashboard(userId, period);
            setDashboard(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load dashboard',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const loadSpending = async () => {
        try {
            setLoading(true);
            const data = await financeAPI.getSpending(userId, { period: 'month' });
            setSpending(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load spending',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const loadPredictions = async () => {
        try {
            setLoading(true);
            const data = await financeAPI.getPredictions(userId);
            setPredictions(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load predictions',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const loadInsights = async () => {
        try {
            setLoading(true);
            const data = await financeAPI.getInsights(userId);
            setInsights(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load insights',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const loadBudgetRecs = async () => {
        try {
            setLoading(true);
            const data = await financeAPI.getBudgetRecommendations(userId);
            setBudgetRecs(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load budget recommendations',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (value: string) => {
        setActiveTab(value);
        if (value === 'spending' && !spending) loadSpending();
        if (value === 'predictions' && !predictions) loadPredictions();
        if (value === 'insights' && !insights) loadInsights();
        if (value === 'budget' && !budgetRecs) loadBudgetRecs();
    };

    const spendingData = dashboard?.spending_by_category
        ? Object.entries(dashboard.spending_by_category).map(([name, value]) => ({
            name,
            value: Number(value),
        }))
        : [];

    const budgetData = dashboard?.vs_budget
        ? Object.entries(dashboard.vs_budget).map(([category, data]: [string, any]) => ({
            category,
            budget: data.budget,
            actual: data.actual,
            difference: data.difference,
        }))
        : [];

    return (
        <Container>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-bold text-black dark:text-white">Personal Finance</h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            Track spending, predictions, and insights
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant={period === 'month' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setPeriod('month')}
                        >
                            Month
                        </Button>
                        <Button
                            variant={period === 'quarter' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setPeriod('quarter')}
                        >
                            Quarter
                        </Button>
                        <Button
                            variant={period === 'year' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setPeriod('year')}
                        >
                            Year
                        </Button>
                    </div>
                </div>

                <Tabs value={activeTab} onValueChange={handleTabChange}>
                    <TabsList>
                        <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                        <TabsTrigger value="spending">Spending</TabsTrigger>
                        <TabsTrigger value="predictions">Predictions</TabsTrigger>
                        <TabsTrigger value="insights">Insights</TabsTrigger>
                        <TabsTrigger value="budget">Budget</TabsTrigger>
                    </TabsList>

                    <TabsContent value="dashboard" className="space-y-6">
                        {loading ? (
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                {[1, 2, 3, 4].map((i) => (
                                    <Skeleton key={i} className="h-32" />
                                ))}
                            </div>
                        ) : dashboard ? (
                            <>
                                {/* Summary Cards */}
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <Card>
                                        <CardHeader className="pb-3">
                                            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                                Income
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="text-2xl font-bold">${dashboard.summary?.income?.toFixed(2) || '0.00'}</div>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardHeader className="pb-3">
                                            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                                Total Spent
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="text-2xl font-bold">${dashboard.summary?.total_spent?.toFixed(2) || '0.00'}</div>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardHeader className="pb-3">
                                            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                                Savings
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                                                ${dashboard.summary?.savings?.toFixed(2) || '0.00'}
                                            </div>
                                        </CardContent>
                                    </Card>
                                    <Card>
                                        <CardHeader className="pb-3">
                                            <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                                Savings Rate
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="text-2xl font-bold">
                                                {((dashboard.summary?.savings_rate || 0) * 100).toFixed(1)}%
                                            </div>
                                        </CardContent>
                                    </Card>
                                </div>

                                {/* Charts */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Spending by Category</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            {spendingData.length > 0 ? (
                                                <ResponsiveContainer width="100%" height={300}>
                                                    <PieChart>
                                                        <Pie
                                                            data={spendingData}
                                                            cx="50%"
                                                            cy="50%"
                                                            labelLine={false}
                                                            label={({ name, percent }) =>
                                                                `${name}: ${(percent * 100).toFixed(0)}%`
                                                            }
                                                            outerRadius={80}
                                                            fill="#8884d8"
                                                            dataKey="value"
                                                        >
                                                            {spendingData.map((entry, index) => (
                                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                            ))}
                                                        </Pie>
                                                        <Tooltip />
                                                    </PieChart>
                                                </ResponsiveContainer>
                                            ) : (
                                                <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                                    No spending data available
                                                </p>
                                            )}
                                        </CardContent>
                                    </Card>

                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Budget vs Actual</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            {budgetData.length > 0 ? (
                                                <ResponsiveContainer width="100%" height={300}>
                                                    <BarChart data={budgetData}>
                                                        <CartesianGrid strokeDasharray="3 3" />
                                                        <XAxis dataKey="category" />
                                                        <YAxis />
                                                        <Tooltip />
                                                        <Legend />
                                                        <Bar dataKey="budget" fill="#666666" />
                                                        <Bar dataKey="actual" fill="#000000" />
                                                    </BarChart>
                                                </ResponsiveContainer>
                                            ) : (
                                                <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                                    No budget data available
                                                </p>
                                            )}
                                        </CardContent>
                                    </Card>
                                </div>

                                {/* Insights */}
                                {dashboard.insights && dashboard.insights.length > 0 && (
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>AI Insights</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="space-y-3">
                                                {dashboard.insights.map((insight: string, index: number) => (
                                                    <div key={index} className="flex items-start gap-3 p-3 border border-gray-200 dark:border-gray-800 rounded-lg">
                                                        <AlertCircle className="h-5 w-5 text-gray-600 dark:text-gray-400 mt-0.5" />
                                                        <p className="text-sm text-gray-700 dark:text-gray-300">{insight}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}
                            </>
                        ) : (
                            <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                No dashboard data available
                            </p>
                        )}
                    </TabsContent>

                    <TabsContent value="spending" className="space-y-6">
                        {loading ? (
                            <Skeleton className="h-64" />
                        ) : spending ? (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Spending Breakdown</CardTitle>
                                    <CardDescription>Total: ${spending.total_spent?.toFixed(2) || '0.00'}</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        {spending.transactions?.map((tx: any, index: number) => (
                                            <div
                                                key={index}
                                                className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-800 rounded-lg"
                                            >
                                                <div>
                                                    <p className="font-medium">{tx.vendor}</p>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                        {tx.category} • {tx.date}
                                                    </p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-bold">${tx.amount?.toFixed(2)}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        ) : (
                            <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                No spending data available
                            </p>
                        )}
                    </TabsContent>

                    <TabsContent value="predictions" className="space-y-6">
                        {loading ? (
                            <Skeleton className="h-64" />
                        ) : predictions ? (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Next Month Prediction</CardTitle>
                                    <CardDescription>Predicted for: {predictions.prediction_for}</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Predicted Total</p>
                                            <p className="text-3xl font-bold">${predictions.predicted_total?.toFixed(2)}</p>
                                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                                                Confidence: {(predictions.confidence_level * 100).toFixed(0)}%
                                            </p>
                                        </div>
                                        {predictions.recommendation && (
                                            <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                                <p className="text-sm font-medium mb-2">Recommendation</p>
                                                <p className="text-sm text-gray-700 dark:text-gray-300">{predictions.recommendation}</p>
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        ) : (
                            <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                No predictions available
                            </p>
                        )}
                    </TabsContent>

                    <TabsContent value="insights" className="space-y-6">
                        {loading ? (
                            <Skeleton className="h-64" />
                        ) : insights ? (
                            <div className="space-y-4">
                                {insights.insights?.map((insight: any, index: number) => (
                                    <Card key={index}>
                                        <CardHeader>
                                            <div className="flex items-center justify-between">
                                                <CardTitle className="text-lg">{insight.type}</CardTitle>
                                                <Badge
                                                    variant={
                                                        insight.severity === 'positive'
                                                            ? 'success'
                                                            : insight.severity === 'medium'
                                                                ? 'warning'
                                                                : 'error'
                                                    }
                                                >
                                                    {insight.severity}
                                                </Badge>
                                            </div>
                                        </CardHeader>
                                        <CardContent>
                                            <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">{insight.message}</p>
                                            {insight.recommendation && (
                                                <p className="text-sm text-gray-600 dark:text-gray-400">{insight.recommendation}</p>
                                            )}
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                No insights available
                            </p>
                        )}
                    </TabsContent>

                    <TabsContent value="budget" className="space-y-6">
                        {loading ? (
                            <Skeleton className="h-64" />
                        ) : budgetRecs ? (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Budget Recommendations</CardTitle>
                                    <CardDescription>
                                        Potential savings: ${budgetRecs.potential_savings?.toFixed(2) || '0.00'} / month
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        {Object.entries(budgetRecs.recommended_budget || {}).map(([category, amount]: [string, any]) => (
                                            <div
                                                key={category}
                                                className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-800 rounded-lg"
                                            >
                                                <div>
                                                    <p className="font-medium capitalize">{category}</p>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                        Current: ${budgetRecs.current_budget?.[category]?.toFixed(2) || '0.00'}
                                                    </p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-bold">${amount?.toFixed(2)}</p>
                                                    <p className="text-xs text-gray-500 dark:text-gray-500">Recommended</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        ) : (
                            <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                No budget recommendations available
                            </p>
                        )}
                    </TabsContent>
                </Tabs>
            </div>
        </Container>
    );
}

