'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { memoryAPI, type WorkspaceStats } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { Search, Database, TrendingUp, FileText, Activity } from 'lucide-react';

export default function InsightsPage() {
    const [workspaceContent, setWorkspaceContent] = useState('');
    const [stats, setStats] = useState<WorkspaceStats | null>(null);
    const [recentEntries, setRecentEntries] = useState<string[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [searching, setSearching] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [memory, statsData, recent] = await Promise.all([
                memoryAPI.getWorkspaceMemory().catch(() => null),
                memoryAPI.getWorkspaceStats().catch(() => null),
                memoryAPI.getRecentEntries(10).catch(() => ({ content: [] })),
            ]);

            if (memory) {
                setWorkspaceContent(memory.workspace_content);
            }
            if (statsData) {
                setStats(statsData.statistics);
            }

            // Ensure recentEntries is always an array
            let entries: string[] = [];
            if (recent) {
                if (Array.isArray(recent)) {
                    entries = recent;
                } else if (recent.content && Array.isArray(recent.content)) {
                    entries = recent.content;
                } else if (typeof recent === 'string') {
                    entries = [recent];
                }
            }
            setRecentEntries(entries);
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

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            toast({
                title: 'Empty query',
                description: 'Please enter a search query',
                variant: 'destructive',
            });
            return;
        }

        try {
            setSearching(true);
            const results = await memoryAPI.searchWorkspace(searchQuery);
            setSearchResults(results);
        } catch (error: any) {
            toast({
                title: 'Search failed',
                description: error.message || 'Failed to search workspace',
                variant: 'destructive',
            });
        } finally {
            setSearching(false);
        }
    };

    return (
        <Container>
            <div className="max-w-6xl mx-auto space-y-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Insights & Memory</h1>
                    <p className="text-gray-600">
                        Explore workspace memory, statistics, and AI-generated insights
                    </p>
                </div>

                {/* Statistics */}
                {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Documents
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.documents_ingested}</div>
                                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Ingested</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Audits
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.audits_performed}</div>
                                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Performed</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Workspace
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.size_kb.toFixed(1)}</div>
                                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">KB</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Lines
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.total_lines}</div>
                                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Total</p>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {/* Search */}
                <Card>
                    <CardHeader>
                        <CardTitle>Search Workspace</CardTitle>
                        <CardDescription>
                            Search through all ingested documents and audit records
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="flex gap-2">
                            <div className="relative flex-1">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                                <Input
                                    placeholder="Search for vendors, amounts, dates, or keywords..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                    className="pl-10"
                                />
                            </div>
                            <Button onClick={handleSearch} disabled={searching}>
                                {searching ? 'Searching...' : 'Search'}
                            </Button>
                        </div>
                        {searchResults && (
                            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                <p className="text-sm font-medium mb-2">
                                    {searchResults.found ? 'Results found' : 'No results'}
                                </p>
                                {searchResults.content && (
                                    <pre className="text-xs whitespace-pre-wrap max-h-64 overflow-auto">
                                        {searchResults.content}
                                    </pre>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Tabs */}
                <Tabs defaultValue="recent" className="w-full">
                    <TabsList>
                        <TabsTrigger value="recent">Recent Entries</TabsTrigger>
                        <TabsTrigger value="workspace">Full Workspace</TabsTrigger>
                    </TabsList>
                    <TabsContent value="recent" className="mt-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Recent Activity</CardTitle>
                                <CardDescription>
                                    Latest {recentEntries.length} entries from workspace
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                {loading ? (
                                    <div className="space-y-4">
                                        <Skeleton className="h-20 w-full" />
                                        <Skeleton className="h-20 w-full" />
                                        <Skeleton className="h-20 w-full" />
                                    </div>
                                ) : Array.isArray(recentEntries) && recentEntries.length > 0 ? (
                                    <div className="space-y-4">
                                        {recentEntries.map((entry, index) => (
                                            <div
                                                key={index}
                                                className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg"
                                            >
                                                <pre className="text-xs whitespace-pre-wrap text-gray-700 dark:text-gray-300">
                                                    {typeof entry === 'string' ? entry : JSON.stringify(entry, null, 2)}
                                                </pre>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                        No recent entries
                                    </p>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>
                    <TabsContent value="workspace" className="mt-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Complete Workspace</CardTitle>
                                <CardDescription>
                                    Full workspace memory content
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                {loading ? (
                                    <div className="space-y-2">
                                        <Skeleton className="h-4 w-full" />
                                        <Skeleton className="h-4 w-full" />
                                        <Skeleton className="h-4 w-3/4" />
                                    </div>
                                ) : workspaceContent ? (
                                    <pre className="text-xs whitespace-pre-wrap max-h-96 overflow-auto p-4 bg-gray-50 dark:bg-gray-900 rounded-lg text-gray-900 dark:text-gray-100">
                                        {workspaceContent}
                                    </pre>
                                ) : (
                                    <p className="text-sm text-gray-600 dark:text-gray-400 text-center py-8">
                                        No workspace content available
                                    </p>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </Container>
    );
}

