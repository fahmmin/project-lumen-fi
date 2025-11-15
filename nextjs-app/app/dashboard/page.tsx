'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { auditAPI, memoryAPI } from '@/services/api';
import { web3Service, AuditRecord } from '@/services/web3';
import { pinataService } from '@/services/pinata';
import { decryptAuditReport } from '@/services/crypto';
import WalletConnect from '@/components/WalletConnect';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { Upload, FileSearch, TrendingUp, Database, ArrowRight, Activity, DollarSign, FileText, AlertTriangle, CheckCircle2, Wallet, XCircle } from 'lucide-react';
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
    AreaChart,
    Area,
} from 'recharts';
import { UnifiedAuditFlow } from '@/components/audit/UnifiedAuditFlow';
import { AuditStatusBadge } from '@/components/financial/AuditStatusBadge';
import { AmountDisplay } from '@/components/financial/AmountDisplay';
import { ITRChecker } from '@/components/financial/ITRChecker';
import { GSTChecker } from '@/components/financial/GSTChecker';

// Vibrant color palette for charts
const CHART_COLORS = [
    '#3B82F6', // Blue
    '#10B981', // Green
    '#F59E0B', // Amber
    '#EF4444', // Red
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#06B6D4', // Cyan
    '#F97316', // Orange
    '#84CC16', // Lime
    '#6366F1', // Indigo
];

const COLORS = CHART_COLORS;
const STATUS_COLORS: Record<string, string> = {
    pass: '#10B981',    // Green
    warning: '#F59E0B', // Amber
    error: '#EF4444',   // Red
    fail: '#DC2626',    // Dark Red
    unknown: '#6B7280', // Gray
};

interface DecryptedAudit {
    auditRecord: AuditRecord;
    decryptedData: any;
    timestamp: Date;
}

export default function Dashboard() {
    const { userId, isConnected, isLoading: userContextLoading } = useUser();
    const [stats, setStats] = useState<any>(null);
    const [recentAudits, setRecentAudits] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [walletAddress, setWalletAddress] = useState<string | null>(null);
    const [contractAddress, setContractAddress] = useState('');
    const [decryptedAudits, setDecryptedAudits] = useState<DecryptedAudit[]>([]);
    const [loadingAudits, setLoadingAudits] = useState(false);
    const [auditStats, setAuditStats] = useState<any>(null);
    const [mongoAudits, setMongoAudits] = useState<any[]>([]);
    const [mongoStats, setMongoStats] = useState<any>(null);
    const { toast } = useToast();

    // Debug: Log userId changes
    useEffect(() => {
        console.log('[Dashboard] UserContext state changed:', {
            userId,
            isConnected,
            userContextLoading,
            timestamp: new Date().toISOString(),
        });
    }, [userId, isConnected, userContextLoading]);

    useEffect(() => {
        loadData();
        checkWalletConnection();
        loadContractAddress();
    }, []);

    useEffect(() => {
        if (walletAddress && contractAddress && web3Service.isContractInitialized()) {
            loadBlockchainAudits();
        }
    }, [walletAddress, contractAddress]);

    // Define loadMongoAudits first using useCallback
    const loadMongoAudits = useCallback(async () => {
        if (!userId) {
            console.log('[Dashboard] No userId, skipping MongoDB load');
            return;
        }

        // Normalize userId to lowercase (wallet addresses should be lowercase)
        const normalizedUserId = userId.toLowerCase().trim();
        console.log('[Dashboard] Normalized userId:', normalizedUserId, '(original:', userId, ')');

        try {
            console.log('[Dashboard] Loading MongoDB audits for userId:', normalizedUserId);
            setLoadingAudits(true);

            const [auditsData, statsData] = await Promise.all([
                auditAPI.getUserAudits(normalizedUserId, 1000).catch((err) => {
                    console.error('[Dashboard] Error fetching user audits:', err);
                    return { audits: [] };
                }),
                auditAPI.getUserAuditStats(normalizedUserId).catch((err) => {
                    console.error('[Dashboard] Error fetching user stats:', err);
                    return null;
                }),
            ]);

            const audits = auditsData?.audits || [];
            console.log('[Dashboard] Loaded MongoDB data:', {
                auditsCount: audits.length,
                auditsDataKeys: Object.keys(auditsData || {}),
                statsData: statsData ? {
                    total_audits: statsData.total_audits,
                    total_amount: statsData.total_amount,
                    keys: Object.keys(statsData),
                } : null,
            });

            // Log first few audits to debug amount field
            if (audits.length > 0) {
                console.log('[Dashboard] Sample audits:', audits.slice(0, 3).map((a: any) => ({
                    audit_id: a.audit_id,
                    amount: a.amount,
                    amountType: typeof a.amount,
                    hasAmount: 'amount' in a,
                    allKeys: Object.keys(a),
                })));
            } else {
                console.log('[Dashboard] No audits found in response');
            }

            setMongoAudits(audits);
            setMongoStats(statsData);

            // Calculate stats purely from MongoDB audits
            if (audits.length > 0) {
                console.log('[Dashboard] Calling calculateStatsFromMongoAudits with', audits.length, 'audits');
                calculateStatsFromMongoAudits(audits);
            } else if (statsData && statsData.total_audits > 0) {
                // Use aggregated stats if available
                console.log('[Dashboard] Using aggregated stats:', statsData);
                calculateStatsFromMongoStats(statsData);
            } else {
                // No data, reset stats
                console.log('[Dashboard] No audit data found - audits.length:', audits.length, 'statsData:', statsData);
                setAuditStats(null);
            }
        } catch (error: any) {
            console.error('[Dashboard] Failed to load MongoDB audits:', error);
            setAuditStats(null);
        } finally {
            setLoadingAudits(false);
        }
    }, [userId]);

    useEffect(() => {
        console.log('[Dashboard] useEffect triggered - userId:', userId, 'userContextLoading:', userContextLoading);

        // Wait for UserContext to finish loading before checking userId
        if (userContextLoading) {
            console.log('[Dashboard] UserContext still loading, waiting...');
            return;
        }

        if (userId) {
            console.log('[Dashboard] userId exists, calling loadMongoAudits');
            loadMongoAudits();
        } else {
            console.log('[Dashboard] No userId after UserContext loaded, not loading MongoDB audits');
        }
    }, [userId, userContextLoading, loadMongoAudits]);

    // Listen for audit saved events to refresh data
    useEffect(() => {
        const handleAuditSaved = () => {
            console.log('[Dashboard] Audit saved event received, refreshing MongoDB data...');
            if (userId) {
                // Small delay to ensure MongoDB has finished saving
                setTimeout(() => {
                    loadMongoAudits();
                }, 500);
            }
        };

        if (typeof window !== 'undefined') {
            window.addEventListener('auditSaved', handleAuditSaved);
            return () => {
                window.removeEventListener('auditSaved', handleAuditSaved);
            };
        }
    }, [userId]);

    const checkWalletConnection = async () => {
        try {
            const address = await web3Service.getAddress();
            if (address) {
                setWalletAddress(address);
            }
        } catch (error) {
            // Not connected
        }
    };

    const loadContractAddress = () => {
        const savedAddress = localStorage.getItem('contractAddress') ||
            (typeof window !== 'undefined' ? process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || '' : '');
        if (savedAddress) {
            setContractAddress(savedAddress);
            if (walletAddress) {
                try {
                    web3Service.initializeContract(savedAddress);
                } catch (error) {
                    // Ignore
                }
            }
        }
    };

    const handleWalletConnect = async (address: string) => {
        setWalletAddress(address);
        try {
            await web3Service.ensureSepoliaNetwork();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to switch to Sepolia network',
                variant: 'destructive',
            });
        }
        if (contractAddress) {
            try {
                web3Service.initializeContract(contractAddress);
                await loadBlockchainAudits();
            } catch (error) {
                // Ignore
            }
        }
    };

    const loadBlockchainAudits = async () => {
        if (!web3Service.isContractInitialized() || !walletAddress) return;

        setLoadingAudits(true);
        try {
            const allAudits = await web3Service.getAllAudits();
            const userAudits = allAudits.filter(
                audit => audit.storedBy.toLowerCase() === walletAddress.toLowerCase()
            );

            // Decrypt user's audits
            const decrypted: DecryptedAudit[] = [];
            for (const audit of userAudits) {
                try {
                    let encryptedData = await pinataService.fetchFromIPFS(audit.pinataLink);

                    // Extract encrypted string
                    if (typeof encryptedData === 'string') {
                        // Already a string
                    } else if (encryptedData && typeof encryptedData === 'object') {
                        if ('pinataContent' in encryptedData) {
                            const pinataContent = encryptedData.pinataContent;
                            if (pinataContent && typeof pinataContent === 'object' && 'encryptedData' in pinataContent) {
                                encryptedData = pinataContent.encryptedData;
                            } else if (typeof pinataContent === 'string') {
                                encryptedData = pinataContent;
                            } else {
                                encryptedData = JSON.stringify(pinataContent);
                            }
                        } else if ('encryptedData' in encryptedData) {
                            encryptedData = encryptedData.encryptedData;
                        } else {
                            const values = Object.values(encryptedData);
                            if (values.length === 1 && typeof values[0] === 'string') {
                                encryptedData = values[0] as string;
                            } else {
                                encryptedData = JSON.stringify(encryptedData);
                            }
                        }
                    } else {
                        encryptedData = String(encryptedData);
                    }

                    if (typeof encryptedData !== 'string') {
                        continue;
                    }

                    const decryptedData = decryptAuditReport(
                        encryptedData,
                        audit.storedBy.toLowerCase(),
                        audit.auditId
                    );

                    decrypted.push({
                        auditRecord: audit,
                        decryptedData,
                        timestamp: new Date(Number(audit.timestamp) * 1000),
                    });
                } catch (error: any) {
                    console.error(`Failed to decrypt audit ${audit.auditId}:`, error);
                    // Continue with other audits
                }
            }

            // Sort by timestamp (newest first)
            decrypted.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
            setDecryptedAudits(decrypted);

            // Calculate statistics
            calculateAuditStats(decrypted);
        } catch (error: any) {
            console.error('Failed to load blockchain audits:', error);
        } finally {
            setLoadingAudits(false);
        }
    };

    const calculateAuditStats = (audits: DecryptedAudit[]) => {
        if (audits.length === 0) {
            setAuditStats(null);
            return;
        }

        // Status distribution
        const statusCounts: Record<string, number> = {};
        const categorySpending: Record<string, { amount: number; count: number }> = {};
        const weeklyData: Record<string, { audits: number; documents: number }> = {};
        let totalAmount = 0;
        let passCount = 0;

        audits.forEach(({ decryptedData, timestamp }) => {
            // Count statuses
            const status = decryptedData?.overall_status || decryptedData?.status || 'unknown';
            statusCounts[status] = (statusCounts[status] || 0) + 1;
            if (status === 'pass') passCount++;

            // Category spending
            const category = decryptedData?.invoice_data?.category || 'Uncategorized';
            const amount = decryptedData?.invoice_data?.amount || 0;
            if (!categorySpending[category]) {
                categorySpending[category] = { amount: 0, count: 0 };
            }
            categorySpending[category].amount += amount;
            categorySpending[category].count += 1;
            totalAmount += amount;

            // Weekly data
            const weekKey = getWeekKey(timestamp);
            if (!weeklyData[weekKey]) {
                weeklyData[weekKey] = { audits: 0, documents: 0 };
            }
            weeklyData[weekKey].audits += 1;
        });

        // Convert to chart format
        const statusDistribution = Object.entries(statusCounts).map(([name, value]) => ({
            name: name.charAt(0).toUpperCase() + name.slice(1),
            value,
            color: STATUS_COLORS[name.toLowerCase()] || '#CCCCCC',
        }));

        const categoryData = Object.entries(categorySpending)
            .map(([category, data]) => ({
                category,
                amount: data.amount,
                count: data.count,
            }))
            .sort((a, b) => b.amount - a.amount)
            .slice(0, 10);

        // Get last 4 weeks
        const weeks = getLastNWeeks(4);
        const auditTrendData = weeks.map(week => ({
            name: week.label,
            audits: weeklyData[week.key]?.audits || 0,
            documents: weeklyData[week.key]?.documents || 0,
        }));

        const successRate = audits.length > 0 ? Math.round((passCount / audits.length) * 100) : 0;

        setAuditStats({
            statusDistribution,
            categoryData,
            auditTrendData,
            successRate,
            totalAudits: audits.length,
            totalAmount,
        });
    };

    const getWeekKey = (date: Date): string => {
        const year = date.getFullYear();
        const week = getWeekNumber(date);
        return `${year}-W${week}`;
    };

    const getWeekNumber = (date: Date): number => {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        return Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
    };

    const getLastNWeeks = (n: number): Array<{ key: string; label: string }> => {
        const weeks: Array<{ key: string; label: string }> = [];
        const now = new Date();
        for (let i = n - 1; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - (i * 7));
            const weekNum = getWeekNumber(date);
            weeks.push({
                key: getWeekKey(date),
                label: `Week ${weekNum}`,
            });
        }
        return weeks;
    };

    const calculateStatsFromMongoAudits = (audits: any[]) => {
        console.log('[Dashboard] Calculating stats from MongoDB audits:', audits.length, 'audits');

        // Status distribution
        const statusCounts: Record<string, number> = {};
        const categorySpending: Record<string, { amount: number; count: number }> = {};
        const weeklyData: Record<string, { audits: number; documents: number }> = {};
        let totalAmount = 0;
        let passCount = 0;

        audits.forEach((audit: any, index: number) => {
            // Use amount field directly from MongoDB document
            const amount = audit.amount || 0;
            console.log(`[Dashboard] Audit ${index + 1}: audit_id=${audit.audit_id}, amount=${amount}, type=${typeof amount}`);
            totalAmount += amount;

            // Count statuses (from audit_report or status field)
            const status = audit.status || audit.audit_report?.overall_status || 'unknown';
            statusCounts[status] = (statusCounts[status] || 0) + 1;
            if (status === 'pass') passCount++;

            // Category spending (from audit_report or category field)
            const category = audit.category || audit.audit_report?.invoice_data?.category || 'Uncategorized';
            if (!categorySpending[category]) {
                categorySpending[category] = { amount: 0, count: 0 };
            }
            categorySpending[category].amount += amount;
            categorySpending[category].count += 1;

            // Weekly data
            const timestamp = audit.timestamp ? new Date(audit.timestamp) : new Date();
            const weekKey = getWeekKey(timestamp);
            if (!weeklyData[weekKey]) {
                weeklyData[weekKey] = { audits: 0, documents: 0 };
            }
            weeklyData[weekKey].audits += 1;
        });

        // Convert to chart format
        const statusDistribution = Object.entries(statusCounts).map(([name, value]) => ({
            name: name.charAt(0).toUpperCase() + name.slice(1),
            value,
            color: STATUS_COLORS[name.toLowerCase()] || '#CCCCCC',
        }));

        const categoryData = Object.entries(categorySpending)
            .map(([category, data]) => ({
                category,
                amount: data.amount,
                count: data.count,
            }))
            .sort((a, b) => b.amount - a.amount)
            .slice(0, 10);

        // Get last 4 weeks
        const weeks = getLastNWeeks(4);
        const auditTrendData = weeks.map(week => ({
            name: week.label,
            audits: weeklyData[week.key]?.audits || 0,
            documents: weeklyData[week.key]?.documents || 0,
        }));

        const successRate = audits.length > 0 ? Math.round((passCount / audits.length) * 100) : 0;

        console.log('[Dashboard] Calculated stats:', {
            totalAudits: audits.length,
            totalAmount,
            successRate,
            statusDistribution: statusCounts,
        });

        const newStats = {
            statusDistribution,
            categoryData,
            auditTrendData,
            successRate,
            totalAudits: audits.length,
            totalAmount,
        };

        console.log('[Dashboard] Setting auditStats to:', newStats);
        setAuditStats(newStats);
        console.log('[Dashboard] auditStats set complete');
    };

    const calculateStatsFromMongoStats = (statsData: any) => {
        // Use aggregated stats from MongoDB
        const statusDistribution = Object.entries(statsData.by_status || {}).map(([name, value]: [string, any]) => ({
            name: name.charAt(0).toUpperCase() + name.slice(1),
            value,
            color: STATUS_COLORS[name.toLowerCase()] || '#CCCCCC',
        }));

        const categoryData = Object.entries(statsData.by_category || {}).map(([category, data]: [string, any]) => ({
            category,
            amount: data.total_amount || 0,
            count: data.count || 0,
        })).sort((a, b) => b.amount - a.amount).slice(0, 10);

        const successRate = statsData.by_status?.pass
            ? Math.round((statsData.by_status.pass / statsData.total_audits) * 100)
            : 0;

        setAuditStats({
            statusDistribution,
            categoryData,
            auditTrendData: auditStats?.auditTrendData || getLastNWeeks(4).map(week => ({
                name: week.label,
                audits: 0,
                documents: 0,
            })),
            successRate,
            totalAudits: statsData.total_audits || 0,
            totalAmount: statsData.total_amount || 0,
        });
    };

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

    // Use real data from auditStats, fallback to empty/default data
    const auditTrendData = auditStats?.auditTrendData || [
        { name: 'Week 1', audits: 0, documents: 0 },
        { name: 'Week 2', audits: 0, documents: 0 },
        { name: 'Week 3', audits: 0, documents: 0 },
        { name: 'Week 4', audits: 0, documents: 0 },
    ];

    const statusDistribution = auditStats?.statusDistribution || [];

    const categoryData = auditStats?.categoryData || [];

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
            <div className="space-y-4 sm:space-y-6 md:space-y-8">
                {/* Header */}
                <div className="flex flex-col gap-3 sm:gap-4">
                    <div>
                        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-black dark:text-white tracking-tight">
                            Dashboard
                        </h1>
                        <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1.5 sm:mt-2">
                            AI Financial Intelligence Overview
                        </p>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                        {!walletAddress && (
                            <div className="w-full sm:w-auto">
                                <WalletConnect onConnect={handleWalletConnect} />
                            </div>
                        )}
                        {walletAddress && (
                            <div className="flex items-center gap-2 px-3 sm:px-4 py-2 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-lg w-fit">
                                <Wallet className="h-4 w-4" />
                                <span className="text-xs sm:text-sm font-medium">
                                    {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
                                </span>
                            </div>
                        )}
                        <div className="w-full sm:w-auto">
                            <UnifiedAuditFlow />
                        </div>
                    </div>
                </div>

                {/* Stats Grid - Mobile optimized */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
                    <Card className="border-gray-200 dark:border-gray-800 hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 px-4 pt-4">
                            <CardTitle className="text-xs sm:text-sm font-medium">Documents</CardTitle>
                            <FileText className="h-4 w-4 text-gray-600 dark:text-gray-400 flex-shrink-0" />
                        </CardHeader>
                        <CardContent className="px-4 pb-4">
                            {loading ? (
                                <Skeleton className="h-7 sm:h-8 w-16 sm:w-20" />
                            ) : (
                                <>
                                    <div className="text-xl sm:text-2xl font-bold tracking-tight">{stats?.documents_ingested || 0}</div>
                                    <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mt-1">Total ingested</p>
                                </>
                            )}
                        </CardContent>
                    </Card>

                    <Card className="border-gray-200 dark:border-gray-800 hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 px-4 pt-4">
                            <CardTitle className="text-xs sm:text-sm font-medium">Blockchain Audits</CardTitle>
                            <FileSearch className="h-4 w-4 text-gray-600 dark:text-gray-400 flex-shrink-0" />
                        </CardHeader>
                        <CardContent className="px-4 pb-4">
                            {loadingAudits ? (
                                <Skeleton className="h-7 sm:h-8 w-16 sm:w-20" />
                            ) : (
                                <>
                                    <div className="text-xl sm:text-2xl font-bold tracking-tight">
                                        {auditStats?.totalAudits || mongoStats?.total_audits || mongoAudits.length || 0}
                                    </div>
                                    <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mt-1 leading-tight">
                                        {userId ? 'Total audits' : 'Connect wallet'}
                                    </p>
                                </>
                            )}
                        </CardContent>
                    </Card>

                    <Card className="border-gray-200 dark:border-gray-800 hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 px-4 pt-4">
                            <CardTitle className="text-xs sm:text-sm font-medium">Workspace</CardTitle>
                            <Database className="h-4 w-4 text-gray-600 dark:text-gray-400 flex-shrink-0" />
                        </CardHeader>
                        <CardContent className="px-4 pb-4">
                            {loading ? (
                                <Skeleton className="h-7 sm:h-8 w-16 sm:w-20" />
                            ) : (
                                <>
                                    <div className="text-xl sm:text-2xl font-bold tracking-tight">{stats?.size_kb?.toFixed(1) || 0}</div>
                                    <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mt-1">KB stored</p>
                                </>
                            )}
                        </CardContent>
                    </Card>

                    <Card className="border-gray-200 dark:border-gray-800 hover:shadow-md transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 px-4 pt-4">
                            <CardTitle className="text-xs sm:text-sm font-medium">Success Rate</CardTitle>
                            <CheckCircle2 className="h-4 w-4 text-gray-600 dark:text-gray-400 flex-shrink-0" />
                        </CardHeader>
                        <CardContent className="px-4 pb-4">
                            {loadingAudits ? (
                                <Skeleton className="h-7 sm:h-8 w-16 sm:w-20" />
                            ) : (
                                <>
                                    <div className="text-xl sm:text-2xl font-bold tracking-tight">{auditStats?.successRate || 85}%</div>
                                    <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mt-1">Audits passed</p>
                                </>
                            )}
                        </CardContent>
                    </Card>

                    <Card className="border-gray-200 dark:border-gray-800 hover:shadow-md transition-shadow col-span-2 sm:col-span-1">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 px-4 pt-4">
                            <CardTitle className="text-xs sm:text-sm font-medium">Total Amount</CardTitle>
                            <DollarSign className="h-4 w-4 text-gray-600 dark:text-gray-400 flex-shrink-0" />
                        </CardHeader>
                        <CardContent className="px-4 pb-4">
                            {loadingAudits ? (
                                <Skeleton className="h-7 sm:h-8 w-20 sm:w-24" />
                            ) : (
                                <>
                                    <div className="text-lg sm:text-xl md:text-2xl font-bold tracking-tight">
                                        ${(() => {
                                            const amount = auditStats?.totalAmount ?? mongoStats?.total_amount ?? 0;
                                            console.log('auditStats', auditStats);
                                            console.log('[Dashboard] Total Amount Display:', {
                                                auditStats_totalAmount: auditStats?.totalAmount,
                                                mongoStats_total_amount: mongoStats?.total_amount,
                                                finalAmount: amount,
                                            });
                                            return amount;
                                        })().toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                                    </div>
                                    <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mt-1">Audited invoices</p>
                                </>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                    {/* Audit Trend */}
                    <Card className="border-gray-200 dark:border-gray-800">
                        <CardHeader className="px-4 sm:px-6 pt-4 sm:pt-6">
                            <CardTitle className="text-base sm:text-lg">Audit & Document Trends</CardTitle>
                            <CardDescription className="text-xs sm:text-sm">Activity over the last 4 weeks</CardDescription>
                        </CardHeader>
                        <CardContent className="px-4 sm:px-6 pb-4 sm:pb-6">
                            <ResponsiveContainer width="100%" height={250} className="sm:h-[300px]">
                                <LineChart data={auditTrendData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
                                    <XAxis
                                        dataKey="name"
                                        className="text-xs"
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                    />
                                    <YAxis
                                        className="text-xs"
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                            border: '1px solid #e5e7eb',
                                            borderRadius: '8px',
                                            padding: '12px',
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                        }}
                                        cursor={{ stroke: '#3B82F6', strokeWidth: 2, strokeDasharray: '5 5' }}
                                    />
                                    <Legend
                                        wrapperStyle={{ paddingTop: '20px' }}
                                        iconType="line"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="audits"
                                        stroke="#3B82F6"
                                        strokeWidth={3}
                                        name="Audits"
                                        dot={{ fill: '#3B82F6', r: 5, strokeWidth: 2, stroke: '#fff' }}
                                        activeDot={{ r: 8, fill: '#2563EB', stroke: '#fff', strokeWidth: 2 }}
                                        animationDuration={1000}
                                        animationEasing="ease-out"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="documents"
                                        stroke="#10B981"
                                        strokeWidth={3}
                                        name="Documents"
                                        dot={{ fill: '#10B981', r: 5, strokeWidth: 2, stroke: '#fff' }}
                                        activeDot={{ r: 8, fill: '#059669', stroke: '#fff', strokeWidth: 2 }}
                                        animationDuration={1000}
                                        animationEasing="ease-out"
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Status Distribution */}
                    <Card className="border-gray-200 dark:border-gray-800">
                        <CardHeader className="px-4 sm:px-6 pt-4 sm:pt-6">
                            <CardTitle className="text-base sm:text-lg">Audit Status Distribution</CardTitle>
                            <CardDescription className="text-xs sm:text-sm">Breakdown of audit results</CardDescription>
                        </CardHeader>
                        <CardContent className="px-4 sm:px-6 pb-4 sm:pb-6">
                            {statusDistribution.length > 0 ? (
                                <ResponsiveContainer width="100%" height={250} className="sm:h-[300px]">
                                    <PieChart>
                                        <Pie
                                            data={statusDistribution}
                                            cx="50%"
                                            cy="50%"
                                            labelLine={false}
                                            label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                                            outerRadius={100}
                                            innerRadius={40}
                                            fill="#8884d8"
                                            dataKey="value"
                                            animationDuration={1000}
                                            paddingAngle={2}
                                        >
                                            {statusDistribution.map((entry: any, index: number) => (
                                                <Cell
                                                    key={`cell-${index}`}
                                                    fill={entry.color}
                                                    stroke={entry.color}
                                                    strokeWidth={2}
                                                />
                                            ))}
                                        </Pie>
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                                border: '1px solid #e5e7eb',
                                                borderRadius: '8px',
                                                padding: '8px',
                                            }}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-[300px] flex items-center justify-center text-gray-500">
                                    {walletAddress ? 'No audit data available' : 'Connect wallet to view status distribution'}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Category Spending - Bar Chart */}
                <Card className="border-gray-200 dark:border-gray-800">
                    <CardHeader className="px-4 sm:px-6 pt-4 sm:pt-6">
                        <CardTitle className="text-base sm:text-lg">Category Spending Analysis</CardTitle>
                        <CardDescription className="text-xs sm:text-sm">Breakdown by category</CardDescription>
                    </CardHeader>
                    <CardContent className="px-4 sm:px-6 pb-4 sm:pb-6">
                        {categoryData.length > 0 ? (
                            <ResponsiveContainer width="100%" height={250} className="sm:h-[300px]">
                                <BarChart data={categoryData} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
                                    <XAxis
                                        dataKey="category"
                                        className="text-xs"
                                        angle={-45}
                                        textAnchor="end"
                                        height={100}
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 11 }}
                                    />
                                    <YAxis
                                        className="text-xs"
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                            border: '1px solid #e5e7eb',
                                            borderRadius: '8px',
                                            padding: '12px',
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                        }}
                                        cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }}
                                        formatter={(value: any, name: string) => {
                                            if (name === 'Amount ($)') {
                                                return [`$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, name];
                                            }
                                            return [value, name];
                                        }}
                                    />
                                    <Legend
                                        wrapperStyle={{ paddingTop: '20px' }}
                                    />
                                    <Bar
                                        dataKey="amount"
                                        name="Amount ($)"
                                        radius={[8, 8, 0, 0]}
                                        animationDuration={1000}
                                        animationEasing="ease-out"
                                    >
                                        {categoryData.map((entry: any, index: number) => (
                                            <Cell
                                                key={`cell-amount-${index}`}
                                                fill={CHART_COLORS[index % CHART_COLORS.length]}
                                                stroke={CHART_COLORS[index % CHART_COLORS.length]}
                                                strokeWidth={1}
                                            />
                                        ))}
                                    </Bar>
                                    <Bar
                                        dataKey="count"
                                        name="Count"
                                        radius={[8, 8, 0, 0]}
                                        animationDuration={1000}
                                        animationEasing="ease-out"
                                    >
                                        {categoryData.map((entry: any, index: number) => (
                                            <Cell
                                                key={`cell-count-${index}`}
                                                fill={CHART_COLORS[(index + 5) % CHART_COLORS.length]}
                                                opacity={0.7}
                                                stroke={CHART_COLORS[(index + 5) % CHART_COLORS.length]}
                                                strokeWidth={1}
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-[300px] flex items-center justify-center text-gray-500">
                                {walletAddress ? 'No category data available' : 'Connect wallet to view category spending'}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Spending Trend - Area Chart */}
                {categoryData.length > 0 && (
                    <Card className="border-gray-200 dark:border-gray-800">
                        <CardHeader className="px-4 sm:px-6 pt-4 sm:pt-6">
                            <CardTitle className="text-base sm:text-lg">Spending Trend by Category</CardTitle>
                            <CardDescription className="text-xs sm:text-sm">Visual spending distribution over categories</CardDescription>
                        </CardHeader>
                        <CardContent className="px-4 sm:px-6 pb-4 sm:pb-6">
                            <ResponsiveContainer width="100%" height={250} className="sm:h-[300px]">
                                <AreaChart data={categoryData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                    <defs>
                                        {categoryData.map((entry: any, index: number) => (
                                            <linearGradient key={`gradient-${index}`} id={`colorAmount${index}`} x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor={CHART_COLORS[index % CHART_COLORS.length]} stopOpacity={0.8} />
                                                <stop offset="95%" stopColor={CHART_COLORS[index % CHART_COLORS.length]} stopOpacity={0.1} />
                                            </linearGradient>
                                        ))}
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
                                    <XAxis
                                        dataKey="category"
                                        className="text-xs"
                                        angle={-45}
                                        textAnchor="end"
                                        height={100}
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 11 }}
                                    />
                                    <YAxis
                                        className="text-xs"
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                            border: '1px solid #e5e7eb',
                                            borderRadius: '8px',
                                            padding: '12px',
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                        }}
                                        formatter={(value: any) => [`$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Amount']}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="amount"
                                        stroke="#3B82F6"
                                        strokeWidth={3}
                                        fill="url(#colorAmount0)"
                                        animationDuration={1000}
                                        animationEasing="ease-out"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                )}

                {/* ITR & GST Checkers */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                    <ITRChecker />
                    <GSTChecker />
                </div>

                {/* Quick Actions & Recent Activity */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                    {/* Quick Actions */}
                    <Card className="border-gray-200 dark:border-gray-800">
                        <CardHeader className="px-4 sm:px-6 pt-4 sm:pt-6">
                            <CardTitle className="text-base sm:text-lg">Quick Actions</CardTitle>
                        </CardHeader>
                        <CardContent className="px-4 sm:px-6 pb-4 sm:pb-6">
                            <div className="space-y-2 sm:space-y-3">
                                {quickActions.map((action) => {
                                    const Icon = action.icon;
                                    return (
                                        <Link key={action.href} href={action.href} className="block active:scale-[0.98] transition-transform">
                                            <div className="flex items-center gap-3 sm:gap-4 p-3 sm:p-4 border border-gray-200 dark:border-gray-800 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors cursor-pointer">
                                                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                                                    <Icon className="h-5 w-5 text-black dark:text-white" />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="font-medium text-sm sm:text-base">{action.title}</p>
                                                    <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5 line-clamp-1">
                                                        {action.description}
                                                    </p>
                                                </div>
                                                <ArrowRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
                                            </div>
                                        </Link>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Recent Activity */}
                    <Card className="border-gray-200 dark:border-gray-800">
                        <CardHeader className="px-4 sm:px-6 pt-4 sm:pt-6">
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-base sm:text-lg">Recent Blockchain Audits</CardTitle>
                                <Link href="/view">
                                    <Button variant="ghost" size="sm" className="text-xs sm:text-sm">
                                        View All
                                        <ArrowRight className="h-3 w-3 sm:h-4 sm:w-4 ml-1 sm:ml-2" />
                                    </Button>
                                </Link>
                            </div>
                        </CardHeader>
                        <CardContent className="px-4 sm:px-6 pb-4 sm:pb-6">
                            {loadingAudits ? (
                                <div className="space-y-3 sm:space-y-4">
                                    <Skeleton className="h-16 sm:h-20 w-full rounded-xl" />
                                    <Skeleton className="h-16 sm:h-20 w-full rounded-xl" />
                                </div>
                            ) : !walletAddress ? (
                                <div className="text-center py-6 sm:py-8">
                                    <Wallet className="h-10 w-10 sm:h-12 sm:w-12 mx-auto text-gray-400 mb-3 sm:mb-4" />
                                    <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-4 px-4">
                                        Connect your wallet to view your blockchain audits
                                    </p>
                                    <div className="px-4">
                                        <WalletConnect onConnect={handleWalletConnect} />
                                    </div>
                                </div>
                            ) : decryptedAudits.length > 0 ? (
                                <div className="space-y-3 sm:space-y-4">
                                    {decryptedAudits.slice(0, 3).map(({ auditRecord, decryptedData, timestamp }, index) => {
                                        const status = decryptedData?.overall_status || 'unknown';
                                        const vendor = decryptedData?.invoice_data?.vendor || 'Unknown Vendor';
                                        const amount = decryptedData?.invoice_data?.amount || 0;
                                        return (
                                            <Link
                                                key={index}
                                                href={`/view`}
                                                className="block p-3 sm:p-4 border border-gray-200 dark:border-gray-800 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-900 transition-all active:scale-[0.98]"
                                            >
                                                <div className="flex items-start justify-between gap-3">
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                                                            <p className="text-xs sm:text-sm font-medium truncate">{auditRecord.auditId}</p>
                                                            <AuditStatusBadge status={status as 'pass' | 'warning' | 'error'} />
                                                        </div>
                                                        <p className="text-xs text-gray-600 dark:text-gray-400 truncate mb-2">
                                                            {vendor}
                                                        </p>
                                                        <div className="flex items-center gap-2 sm:gap-3 text-xs text-gray-500 flex-wrap">
                                                            <AmountDisplay amount={amount} size="sm" />
                                                            <span>•</span>
                                                            <span>{timestamp.toLocaleDateString()}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </Link>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div className="text-center py-6 sm:py-8">
                                    <FileSearch className="h-10 w-10 sm:h-12 sm:w-12 mx-auto text-gray-400 mb-3 sm:mb-4" />
                                    <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 px-4">
                                        No blockchain audits found. Store your first audit to see it here.
                                    </p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </Container>
    );
}

