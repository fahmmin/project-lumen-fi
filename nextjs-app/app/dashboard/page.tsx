'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { auditAPI, memoryAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { Upload, FileSearch, TrendingUp, Database, ArrowRight, Activity, DollarSign, FileText, AlertTriangle, CheckCircle2 } from 'lucide-react';
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
import { UnifiedAuditFlow } from '@/components/audit/UnifiedAuditFlow';

const COLORS = ['#000000', '#666666', '#999999', '#CCCCCC'];

export default function Dashboard() {
    const [stats, setStats] = useState<any>(null);
    const [recentAudits, setRecentAudits] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [statsData, auditHistory] = await Promise.all([
                memoryAPI.getWorkspaceStats().catch(() => null),
                auditAPI.getAuditHistory(10).catch(() => ({ content: [] })),
            ]);

            setStats(statsData?.statistics || null);

            // Ensure recentAudits is always an array
            let audits: any[] = [];
            if (auditHistory) {
                if (Array.isArray(auditHistory)) {
                    audits = auditHistory;
                } else if (auditHistory.content && Array.isArray(auditHistory.content)) {
                    audits = auditHistory.content;
                } else if (typeof auditHistory === 'string') {
                    audits = [auditHistory];
                }
            }
            setRecentAudits(audits);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load dashboard data',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    // Mock data for charts (replace with real data when available)
    const auditTrendData = [
        { name: 'Week 1', audits: 12, documents: 8 },
        { name: 'Week 2', audits: 19, documents: 15 },
        { name: 'Week 3', audits: 15, documents: 12 },
        { name: 'Week 4', audits: 22, documents: 18 },
    ];

    const statusDistribution = [
        { name: 'Pass', value: 45, color: '#000000' },
        { name: 'Warning', value: 25, color: '#666666' },
        { name: 'Error', value: 10, color: '#999999' },
    ];

    const categoryData = [
        { category: 'Office Supplies', amount: 4500, count: 12 },
        { category: 'Travel', amount: 3200, count: 8 },
        { category: 'Software', amount: 2800, count: 5 },
        { category: 'Utilities', amount: 1500, count: 4 },
    ];

    const quickActions = [
        {
            title: 'Upload Document',
            description: 'Upload and process financial documents',
            href: '/upload',
            icon: Upload,
        },
        {
            title: 'View Insights',
            description: 'Explore AI-generated insights',
            href: '/insights',
            icon: TrendingUp,
        },
        {
            title: 'Documents',
            description: 'Manage your documents',
            href: '/documents',
            icon: Database,
        },
    ];

    return (
        <Container>
            <div className="space-y-6 md:space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-bold text-black dark:text-white">Dashboard</h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            AI Financial Intelligence Overview
                        </p>
                    </div>
                    <UnifiedAuditFlow />
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Documents</CardTitle>
                            <FileText className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                        </CardHeader>
                        <CardContent>
                            {loading ? (
                                <Skeleton className="h-8 w-20" />
                            ) : (
                                <>
                                    <div className="text-2xl font-bold">{stats?.documents_ingested || 0}</div>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Total ingested</p>
                                </>
                            )}
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Audits</CardTitle>
                            <FileSearch className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                        </CardHeader>
                        <CardContent>
                            {loading ? (
                                <Skeleton className="h-8 w-20" />
                            ) : (
                                <>
                                    <div className="text-2xl font-bold">{stats?.audits_performed || 0}</div>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Total performed</p>
                                </>
                            )}
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Workspace</CardTitle>
                            <Database className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                        </CardHeader>
                        <CardContent>
                            {loading ? (
                                <Skeleton className="h-8 w-20" />
                            ) : (
                                <>
                                    <div className="text-2xl font-bold">{stats?.size_kb?.toFixed(1) || 0}</div>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">KB stored</p>
                                </>
                            )}
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                            <CheckCircle2 className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                        </CardHeader>
                        <CardContent>
                            {loading ? (
                                <Skeleton className="h-8 w-20" />
                            ) : (
                                <>
                                    <div className="text-2xl font-bold">85%</div>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">Audits passed</p>
                                </>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Audit Trend */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Audit & Document Trends</CardTitle>
                            <CardDescription>Activity over the last 4 weeks</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={auditTrendData}>
                                    <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-800" />
                                    <XAxis dataKey="name" className="text-xs" />
                                    <YAxis className="text-xs" />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'var(--background)',
                                            border: '1px solid var(--border)',
                                        }}
                                    />
                                    <Legend />
                                    <Line
                                        type="monotone"
                                        dataKey="audits"
                                        stroke="#000000"
                                        strokeWidth={2}
                                        name="Audits"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="documents"
                                        stroke="#666666"
                                        strokeWidth={2}
                                        name="Documents"
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Status Distribution */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Audit Status Distribution</CardTitle>
                            <CardDescription>Breakdown of audit results</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={statusDistribution}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {statusDistribution.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </div>

                {/* Category Spending */}
                <Card>
                    <CardHeader>
                        <CardTitle>Category Spending Analysis</CardTitle>
                        <CardDescription>Breakdown by category</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={categoryData}>
                                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-800" />
                                <XAxis dataKey="category" className="text-xs" />
                                <YAxis className="text-xs" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--background)',
                                        border: '1px solid var(--border)',
                                    }}
                                />
                                <Legend />
                                <Bar dataKey="amount" fill="#000000" name="Amount ($)" />
                                <Bar dataKey="count" fill="#666666" name="Count" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Quick Actions & Recent Activity */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Quick Actions */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Quick Actions</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {quickActions.map((action) => {
                                    const Icon = action.icon;
                                    return (
                                        <Link key={action.href} href={action.href}>
                                            <div className="flex items-center gap-4 p-3 border border-gray-200 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors cursor-pointer">
                                                <Icon className="h-5 w-5 text-black dark:text-white" />
                                                <div className="flex-1">
                                                    <p className="font-medium">{action.title}</p>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                        {action.description}
                                                    </p>
                                                </div>
                                                <ArrowRight className="h-4 w-4 text-gray-400" />
                                            </div>
                                        </Link>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Recent Activity */}
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <CardTitle>Recent Activity</CardTitle>
                                <Link href="/insights">
                                    <Button variant="ghost" size="sm">
                                        View All
                                        <ArrowRight className="h-4 w-4 ml-2" />
                                    </Button>
                                </Link>
                            </div>
                        </CardHeader>
                        <CardContent>
                            {loading ? (
                                <div className="space-y-4">
                                    <Skeleton className="h-16 w-full" />
                                    <Skeleton className="h-16 w-full" />
                                </div>
                            ) : Array.isArray(recentAudits) && recentAudits.length > 0 ? (
                                <div className="space-y-4">
                                    {recentAudits.slice(0, 3).map((audit: any, index: number) => {
                                        const auditText = typeof audit === 'string' ? audit : JSON.stringify(audit);
                                        return (
                                            <div
                                                key={index}
                                                className="p-3 border border-gray-200 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors"
                                            >
                                                <div className="flex items-center justify-between">
                                                    <div>
                                                        <p className="text-sm font-medium">
                                                            {auditText.includes?.('AUDIT RUN') ? 'Audit' : 'Document'}
                                                        </p>
                                                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                                                            {auditText.substring(0, 100)}...
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <p className="text-sm text-gray-600 dark:text-gray-400">No recent activity</p>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </Container>
    );
}

