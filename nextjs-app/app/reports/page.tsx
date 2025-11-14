'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { reportsAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { FileText, Download, Loader2, Calendar, FileDown, Wallet } from 'lucide-react';

export default function ReportsPage() {
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [reportHistory, setReportHistory] = useState<any[]>([]);
    const [generating, setGenerating] = useState(false);
    const [reportType, setReportType] = useState<string>('monthly_summary');
    const [period, setPeriod] = useState<string>('month');
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    const loadHistory = async () => {
        if (!userId) return;
        setLoading(true);
        try {
            const data = await reportsAPI.getReportHistory(userId, 20);
            setReportHistory(data.reports || []);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load report history',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadHistory();
    }, [userId]);

    const handleGenerateReport = async () => {
        if (!userId) {
            toast({
                title: 'Error',
                description: 'Please enter a user ID',
                variant: 'destructive',
            });
            return;
        }

        setGenerating(true);
        try {
            const result = await reportsAPI.generateReport(userId, reportType, period);
            toast({
                title: 'Report Generated!',
                description: 'Your report is ready for download',
                variant: 'success',
            });
            loadHistory();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to generate report',
                variant: 'destructive',
            });
        } finally {
            setGenerating(false);
        }
    };

    const handleDownload = async (filename: string) => {
        try {
            const blob = await reportsAPI.downloadReport(filename);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            toast({
                title: 'Download Started',
                description: 'Your report is downloading',
                variant: 'success',
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to download report',
                variant: 'destructive',
            });
        }
    };

    return (
        <Container>
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold mb-2">Financial Reports</h1>
                    <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                        Generate and download AI-powered financial reports
                    </p>
                </div>

                {/* Generate Report */}
                <Card>
                    <CardHeader>
                        <CardTitle>Generate New Report</CardTitle>
                        <CardDescription>Create a comprehensive financial report</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {!isConnected && (
                            <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-sm text-yellow-800 dark:text-yellow-200">
                                Please connect your wallet to generate reports
                            </div>
                        )}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium mb-2 block">Report Type</label>
                                <select
                                    value={reportType}
                                    onChange={(e) => setReportType(e.target.value)}
                                    className="w-full px-3 py-2 border rounded-lg"
                                >
                                    <option value="monthly_summary">Monthly Summary</option>
                                    <option value="spending_analysis">Spending Analysis</option>
                                    <option value="goal_progress">Goal Progress</option>
                                    <option value="tax_summary">Tax Summary</option>
                                </select>
                            </div>
                            <div>
                                <label className="text-sm font-medium mb-2 block">Period</label>
                                <select
                                    value={period}
                                    onChange={(e) => setPeriod(e.target.value)}
                                    className="w-full px-3 py-2 border rounded-lg"
                                >
                                    <option value="month">Month</option>
                                    <option value="quarter">Quarter</option>
                                    <option value="year">Year</option>
                                </select>
                            </div>
                        </div>
                        <Button onClick={handleGenerateReport} disabled={generating || !isConnected || !userId} className="w-full">
                            {generating ? (
                                <>
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <FileText className="h-4 w-4 mr-2" />
                                    Generate Report
                                </>
                            )}
                        </Button>
                    </CardContent>
                </Card>

                {/* Report History */}
                <Card>
                    <CardHeader>
                        <CardTitle>Report History</CardTitle>
                        <CardDescription>Previously generated reports</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {!isConnected ? (
                            <div className="text-center py-12">
                                <Wallet className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                                <p className="text-gray-600 dark:text-gray-400 mb-4">
                                    Connect your wallet to view report history
                                </p>
                                <Button onClick={connectWallet}>
                                    <Wallet className="h-4 w-4 mr-2" />
                                    Connect Wallet
                                </Button>
                            </div>
                        ) : userLoading || loading ? (
                            <Skeleton className="h-32 w-full" />
                        ) : reportHistory.length > 0 ? (
                            <div className="space-y-2">
                                {reportHistory.map((report, index) => (
                                    <div
                                        key={index}
                                        className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-800 rounded-lg"
                                    >
                                        <div className="flex items-center gap-3">
                                            <FileText className="h-5 w-5 text-gray-400" />
                                            <div>
                                                <p className="font-semibold">{report.filename}</p>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                                    {new Date(report.created_at * 1000).toLocaleString()} •{' '}
                                                    {(report.size_bytes / 1024).toFixed(2)} KB
                                                </p>
                                            </div>
                                        </div>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleDownload(report.filename)}
                                        >
                                            <Download className="h-4 w-4 mr-2" />
                                            Download
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12">
                                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                                <p className="text-gray-600 dark:text-gray-400">
                                    No reports generated yet. Create your first report above!
                                </p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </Container>
    );
}

