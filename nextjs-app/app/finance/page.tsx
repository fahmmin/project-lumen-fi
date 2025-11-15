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
import { useUser } from '@/contexts/UserContext';
import { DollarSign, TrendingUp, TrendingDown, Target, AlertCircle, CheckCircle2, Wallet } from 'lucide-react';
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
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [dashboard, setDashboard] = useState<any>(null);
    const [spending, setSpending] = useState<any>(null);
    const [predictions, setPredictions] = useState<any>(null);
    const [insights, setInsights] = useState<any>(null);
    const [budgetRecs, setBudgetRecs] = useState<any>(null);
    const [analytics, setAnalytics] = useState<any>(null);
    const [savingsOpportunities, setSavingsOpportunities] = useState<any>(null);
    const [trends, setTrends] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('dashboard');
    const [period, setPeriod] = useState<'month' | 'quarter' | 'year'>('month');
    const [selectedCategory, setSelectedCategory] = useState<string>('');
    const { toast } = useToast();

    useEffect(() => {
        if (userId) {
            loadDashboard();
        }
    }, [period, userId]);

    const loadDashboard = async () => {
        if (!userId) return;
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
        if (!userId) return;
        try {
            setLoading(true);
            // Calculate date range based on period
            const endDate = new Date();
            const startDate = new Date();
            if (period === 'month') {
                startDate.setMonth(startDate.getMonth() - 1);
            } else if (period === 'quarter') {
                startDate.setMonth(startDate.getMonth() - 3);
            } else if (period === 'year') {
                startDate.setFullYear(startDate.getFullYear() - 1);
            }
            const data = await financeAPI.getSpending(userId, {
                start_date: startDate.toISOString().split('T')[0],
                end_date: endDate.toISOString().split('T')[0],
            });
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
        if (!userId) return;
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
        if (!userId) return;
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
        if (!userId) return;
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

    const loadMonthlyAnalytics = async () => {
        if (!userId) return;
        try {
            setLoading(true);
            const now = new Date();
            const data = await financeAPI.getMonthlyAnalysis(userId, now.getFullYear(), now.getMonth() + 1);
            setAnalytics(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load monthly analytics',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const loadSavingsOpportunities = async () => {
        if (!userId) return;
        try {
            setLoading(true);
            const data = await financeAPI.getSavingsOpportunities(userId);
            setSavingsOpportunities(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load savings opportunities',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const loadTrends = async () => {
        if (!userId) return;
        try {
            setLoading(true);
            const data = await financeAPI.getSpendingTrends(userId, 6);
            setTrends(data);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load spending trends',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (value: string) => {
        setActiveTab(value);
        if (value === 'spending' && !spending) {
            loadSpending();
        }
        if (value === 'predictions' && !predictions) {
            loadPredictions();
        }
        if (value === 'insights' && !insights) {
            loadInsights();
        }
        if (value === 'budget' && !budgetRecs) {
            loadBudgetRecs();
        }
        if (value === 'analytics') {
            if (!analytics) loadMonthlyAnalytics();
            if (!savingsOpportunities) loadSavingsOpportunities();
            if (!trends) loadTrends();
        }
    };

    // Reload spending when period changes (only if spending tab is active)
    useEffect(() => {
        if (userId && activeTab === 'spending' && spending) {
            loadSpending();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [period]);

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
                {!isConnected && (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <Wallet className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                            <p className="text-gray-600 dark:text-gray-400 mb-4">
                                Connect your wallet to view financial dashboard
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

                        <Tabs defaultValue={activeTab} onValueChange={handleTabChange}>
                            <TabsList>
                                <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                                <TabsTrigger value="spending">Spending</TabsTrigger>
                                <TabsTrigger value="analytics">Analytics</TabsTrigger>
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
                                                                    label={(props: any) => {
                                                                        const name = props.name || '';
                                                                        const percent = props.percent || 0;
                                                                        return `${name}: ${(percent * 100).toFixed(0)}%`;
                                                                    }}
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

                            <TabsContent value="analytics" className="space-y-6">
                                {loading ? (
                                    <Skeleton className="h-64" />
                                ) : (
                                    <>
                                        {/* Monthly Analytics Section */}
                                        {analytics && (
                                            <Card>
                                                <CardHeader>
                                                    <CardTitle>This Month's Analysis</CardTitle>
                                                    <CardDescription>{analytics.month}</CardDescription>
                                                </CardHeader>
                                                <CardContent className="space-y-4">
                                                    {/* Summary Stats */}
                                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                        <div className="p-3 border rounded-lg">
                                                            <p className="text-xs text-gray-600 dark:text-gray-400">Total Spent</p>
                                                            <p className="text-xl font-bold">${analytics.summary?.total_spent?.toFixed(2)}</p>
                                                        </div>
                                                        <div className="p-3 border rounded-lg">
                                                            <p className="text-xs text-gray-600 dark:text-gray-400">Transactions</p>
                                                            <p className="text-xl font-bold">{analytics.summary?.total_transactions}</p>
                                                        </div>
                                                        <div className="p-3 border rounded-lg">
                                                            <p className="text-xs text-gray-600 dark:text-gray-400">Savings</p>
                                                            <p className="text-xl font-bold text-green-600">${analytics.summary?.savings?.toFixed(2)}</p>
                                                        </div>
                                                        <div className="p-3 border rounded-lg">
                                                            <p className="text-xs text-gray-600 dark:text-gray-400">vs Last Month</p>
                                                            <p className={`text-xl font-bold ${analytics.vs_previous_month?.trend === 'increasing' ? 'text-red-600' : 'text-green-600'}`}>
                                                                {analytics.vs_previous_month?.percent_change > 0 ? '+' : ''}{analytics.vs_previous_month?.percent_change?.toFixed(1)}%
                                                            </p>
                                                        </div>
                                                    </div>

                                                    {/* Weekly Breakdown */}
                                                    {analytics.weekly_breakdown && analytics.weekly_breakdown.length > 0 && (
                                                        <div>
                                                            <h3 className="font-semibold mb-3">Weekly Breakdown</h3>
                                                            <div className="space-y-2">
                                                                {analytics.weekly_breakdown.map((week: any, idx: number) => (
                                                                    <div key={idx} className="flex items-center justify-between p-3 border rounded">
                                                                        <div>
                                                                            <p className="font-medium">{week.week}</p>
                                                                            <p className="text-sm text-gray-600">{week.count} transactions</p>
                                                                        </div>
                                                                        <p className="font-bold">${week.total?.toFixed(2)}</p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Top Expenses */}
                                                    {analytics.top_expenses && analytics.top_expenses.length > 0 && (
                                                        <div>
                                                            <h3 className="font-semibold mb-3">Top Expenses</h3>
                                                            <div className="space-y-2">
                                                                {analytics.top_expenses.slice(0, 5).map((expense: any, idx: number) => (
                                                                    <div key={idx} className="flex items-center justify-between p-3 border rounded">
                                                                        <div>
                                                                            <p className="font-medium">{expense.vendor}</p>
                                                                            <p className="text-sm text-gray-600">{expense.category} • {expense.date}</p>
                                                                        </div>
                                                                        <p className="font-bold text-red-600">${expense.amount?.toFixed(2)}</p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Insights */}
                                                    {analytics.insights && analytics.insights.length > 0 && (
                                                        <div>
                                                            <h3 className="font-semibold mb-3">AI Insights</h3>
                                                            <div className="space-y-2">
                                                                {analytics.insights.map((insight: string, idx: number) => (
                                                                    <div key={idx} className="flex items-start gap-2 p-3 bg-gray-50 dark:bg-gray-900 rounded">
                                                                        <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                                                                        <p className="text-sm">{insight}</p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Recommendations */}
                                                    {analytics.recommendations && analytics.recommendations.length > 0 && (
                                                        <div>
                                                            <h3 className="font-semibold mb-3">Recommendations</h3>
                                                            <div className="space-y-2">
                                                                {analytics.recommendations.map((rec: string, idx: number) => (
                                                                    <div key={idx} className="flex items-start gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded">
                                                                        <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5" />
                                                                        <p className="text-sm">{rec}</p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                </CardContent>
                                            </Card>
                                        )}

                                        {/* Savings Opportunities Section */}
                                        {savingsOpportunities && (
                                            <Card>
                                                <CardHeader>
                                                    <CardTitle>Savings Opportunities</CardTitle>
                                                    <CardDescription>
                                                        Potential to save ${savingsOpportunities.total_savings_potential?.toFixed(2)}/month
                                                        (${savingsOpportunities.annual_savings_potential?.toFixed(2)}/year)
                                                    </CardDescription>
                                                </CardHeader>
                                                <CardContent className="space-y-4">
                                                    {/* Goal Impact */}
                                                    {savingsOpportunities.goal_impact?.goals_impacted > 0 && (
                                                        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                                            <h3 className="font-semibold mb-2">Impact on Your Goals</h3>
                                                            <div className="space-y-2">
                                                                {savingsOpportunities.goal_impact.impact.map((goal: any, idx: number) => (
                                                                    <p key={idx} className="text-sm">
                                                                        <strong>{goal.goal_name}:</strong> Reach {goal.time_saved_months?.toFixed(1)} months earlier ({goal.accelerated_by})
                                                                    </p>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Strategy */}
                                                    {savingsOpportunities.strategy && savingsOpportunities.strategy.length > 0 && (
                                                        <div>
                                                            <h3 className="font-semibold mb-3">Savings Strategy</h3>
                                                            <div className="space-y-2">
                                                                {savingsOpportunities.strategy.map((strategy: string, idx: number) => (
                                                                    <div key={idx} className="flex items-start gap-2 p-3 border rounded">
                                                                        <Target className="h-4 w-4 text-green-600 mt-0.5" />
                                                                        <p className="text-sm">{strategy}</p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Priority Actions */}
                                                    {savingsOpportunities.priority_actions && savingsOpportunities.priority_actions.length > 0 && (
                                                        <div>
                                                            <h3 className="font-semibold mb-3">Priority Actions</h3>
                                                            <div className="space-y-2">
                                                                {savingsOpportunities.priority_actions.map((action: string, idx: number) => (
                                                                    <div key={idx} className="flex items-start gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded">
                                                                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-yellow-500 text-white text-xs font-bold">{idx + 1}</span>
                                                                        <p className="text-sm flex-1">{action}</p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Category Opportunities */}
                                                    {savingsOpportunities.opportunities_by_category && Object.keys(savingsOpportunities.opportunities_by_category).length > 0 && (
                                                        <div>
                                                            <h3 className="font-semibold mb-3">By Category</h3>
                                                            <div className="space-y-3">
                                                                {Object.entries(savingsOpportunities.opportunities_by_category).map(([category, opp]: [string, any]) => (
                                                                    <div key={category} className="p-4 border rounded-lg">
                                                                        <div className="flex items-center justify-between mb-2">
                                                                            <h4 className="font-medium capitalize">{category}</h4>
                                                                            <Badge variant="secondary">Save ${opp.savings_potential?.toFixed(2)}/mo</Badge>
                                                                        </div>
                                                                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                                                                            Current: ${opp.current_monthly?.toFixed(2)}/mo • Budget: ${opp.budget?.toFixed(2)}/mo
                                                                        </p>
                                                                        {opp.strategies && opp.strategies.length > 0 && (
                                                                            <ul className="text-sm space-y-1">
                                                                                {opp.strategies.map((strategy: string, idx: number) => (
                                                                                    <li key={idx} className="text-gray-700 dark:text-gray-300">• {strategy}</li>
                                                                                ))}
                                                                            </ul>
                                                                        )}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                </CardContent>
                                            </Card>
                                        )}

                                        {/* Trends Section */}
                                        {trends && trends.monthly_totals && (
                                            <Card>
                                                <CardHeader>
                                                    <CardTitle>Spending Trends ({trends.months_analyzed} months)</CardTitle>
                                                </CardHeader>
                                                <CardContent className="space-y-4">
                                                    {/* Month-by-Month */}
                                                    <div>
                                                        <h3 className="font-semibold mb-3">Monthly Totals</h3>
                                                        <ResponsiveContainer width="100%" height={250}>
                                                            <LineChart data={Object.entries(trends.monthly_totals).map(([month, data]: [string, any]) => ({
                                                                month,
                                                                total: data.total
                                                            }))}>
                                                                <CartesianGrid strokeDasharray="3 3" />
                                                                <XAxis dataKey="month" />
                                                                <YAxis />
                                                                <Tooltip />
                                                                <Legend />
                                                                <Line type="monotone" dataKey="total" stroke="#000000" name="Total Spent" />
                                                            </LineChart>
                                                        </ResponsiveContainer>
                                                    </div>

                                                    {/* Volatility */}
                                                    {trends.volatility && (
                                                        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                                            <h3 className="font-semibold mb-2">Spending Consistency</h3>
                                                            <p className="text-sm mb-1">
                                                                <strong>Level:</strong> {trends.volatility.volatility_level?.replace('_', ' ')}
                                                            </p>
                                                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                                                {trends.volatility.description}
                                                            </p>
                                                        </div>
                                                    )}

                                                    {/* Growth Analysis */}
                                                    {trends.growth_analysis && (
                                                        <div className="p-4 border rounded-lg">
                                                            <h3 className="font-semibold mb-2">Trend Analysis</h3>
                                                            <p className="text-sm mb-2">
                                                                Overall trend: <Badge variant={trends.growth_analysis.overall_trend === 'increasing' ? 'destructive' : 'default'}>
                                                                    {trends.growth_analysis.overall_trend}
                                                                </Badge>
                                                            </p>
                                                            <p className="text-sm">
                                                                Total change: {trends.growth_analysis.percent_change > 0 ? '+' : ''}{trends.growth_analysis.percent_change?.toFixed(1)}%
                                                            </p>
                                                            {trends.growth_analysis.fastest_growing_categories && trends.growth_analysis.fastest_growing_categories.length > 0 && (
                                                                <div className="mt-3">
                                                                    <p className="text-sm font-medium mb-1">Fastest growing categories:</p>
                                                                    <ul className="text-sm text-gray-600 dark:text-gray-400">
                                                                        {trends.growth_analysis.fastest_growing_categories.map((cat: any, idx: number) => (
                                                                            <li key={idx}>• {cat.category}: +${cat.change?.toFixed(2)}</li>
                                                                        ))}
                                                                    </ul>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}

                                                    {/* Seasonal Patterns */}
                                                    {trends.seasonal_patterns?.seasonal && (
                                                        <div className="p-4 border rounded-lg">
                                                            <h3 className="font-semibold mb-2">Seasonal Patterns Detected</h3>
                                                            {trends.seasonal_patterns.high_spending_months && Object.keys(trends.seasonal_patterns.high_spending_months).length > 0 && (
                                                                <div className="mb-2">
                                                                    <p className="text-sm font-medium">High spending months:</p>
                                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                                        {Object.entries(trends.seasonal_patterns.high_spending_months).map(([month, amt]: [string, any]) => `${month} ($${amt.toFixed(2)})`).join(', ')}
                                                                    </p>
                                                                </div>
                                                            )}
                                                            {trends.seasonal_patterns.low_spending_months && Object.keys(trends.seasonal_patterns.low_spending_months).length > 0 && (
                                                                <div>
                                                                    <p className="text-sm font-medium">Low spending months:</p>
                                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                                        {Object.entries(trends.seasonal_patterns.low_spending_months).map(([month, amt]: [string, any]) => `${month} ($${amt.toFixed(2)})`).join(', ')}
                                                                    </p>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </CardContent>
                                            </Card>
                                        )}
                                    </>
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
                    </>
                )}
            </div>
        </Container>
    );
}

