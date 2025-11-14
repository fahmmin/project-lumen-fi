'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { remindersAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { Bell, Calendar, DollarSign, TrendingUp, X, Clock, Wallet } from 'lucide-react';

export default function RemindersPage() {
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [reminders, setReminders] = useState<any[]>([]);
    const [patterns, setPatterns] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        if (userId) {
            loadData();
        }
    }, [userId]);

    const loadData = async () => {
        try {
            setLoading(true);
            if (!userId) return;
            const [remindersData, patternsData] = await Promise.all([
                remindersAPI.getReminders(userId).catch(() => ({ reminders: [] })),
                remindersAPI.getPatterns(userId).catch(() => ({ patterns: [] })),
            ]);
            setReminders(remindersData.reminders || []);
            setPatterns(patternsData.patterns || []);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load reminders',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleDismiss = async (reminderId: string) => {
        try {
            // Note: Backend doesn't support dismissing reminders yet
            // For now, just reload data to refresh the list
            toast({
                title: 'Info',
                description: 'Dismissing reminders is not yet supported. Reminders are generated dynamically.',
                variant: 'default',
            });
            // await remindersAPI.dismissReminder(reminderId);
            // loadData();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to dismiss reminder',
                variant: 'destructive',
            });
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
                                Connect your wallet to view reminders
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
                            <h1 className="text-3xl md:text-4xl font-bold text-black dark:text-white">Reminders & Patterns</h1>
                            <p className="text-gray-600 dark:text-gray-400 mt-2">
                                Smart purchase reminders and spending patterns
                            </p>
                        </div>

                        <Tabs defaultValue="reminders">
                            <TabsList>
                                <TabsTrigger value="reminders">Reminders</TabsTrigger>
                                <TabsTrigger value="patterns">Patterns</TabsTrigger>
                            </TabsList>

                            <TabsContent value="reminders" className="space-y-4">
                                {loading ? (
                                    <div className="space-y-4">
                                        {[1, 2, 3].map((i) => (
                                            <Skeleton key={i} className="h-32" />
                                        ))}
                                    </div>
                                ) : reminders.length > 0 ? (
                                    reminders.map((reminder) => (
                                        <Card key={reminder.reminder_id}>
                                            <CardHeader>
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-3">
                                                        <Bell className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                                                        <CardTitle className="text-lg">{reminder.type.replace('_', ' ')}</CardTitle>
                                                    </div>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => handleDismiss(reminder.reminder_id)}
                                                    >
                                                        <X className="h-4 w-4" />
                                                    </Button>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">{reminder.message}</p>
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                    {reminder.category && (
                                                        <div>
                                                            <p className="text-gray-600 dark:text-gray-400">Category</p>
                                                            <p className="font-medium capitalize">{reminder.category}</p>
                                                        </div>
                                                    )}
                                                    {reminder.typical_amount && (
                                                        <div>
                                                            <p className="text-gray-600 dark:text-gray-400">Typical Amount</p>
                                                            <p className="font-medium">${reminder.typical_amount.toFixed(2)}</p>
                                                        </div>
                                                    )}
                                                    {reminder.next_expected_date && (
                                                        <div>
                                                            <p className="text-gray-600 dark:text-gray-400">Next Expected</p>
                                                            <p className="font-medium">{new Date(reminder.next_expected_date).toLocaleDateString()}</p>
                                                        </div>
                                                    )}
                                                    {reminder.confidence && (
                                                        <div>
                                                            <p className="text-gray-600 dark:text-gray-400">Confidence</p>
                                                            <p className="font-medium">{(reminder.confidence * 100).toFixed(0)}%</p>
                                                        </div>
                                                    )}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))
                                ) : (
                                    <Card>
                                        <CardContent className="pt-6">
                                            <div className="text-center py-8">
                                                <Bell className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600 mb-4" />
                                                <p className="text-sm text-gray-600 dark:text-gray-400">No active reminders</p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}
                            </TabsContent>

                            <TabsContent value="patterns" className="space-y-4">
                                {loading ? (
                                    <div className="space-y-4">
                                        {[1, 2, 3].map((i) => (
                                            <Skeleton key={i} className="h-32" />
                                        ))}
                                    </div>
                                ) : patterns.length > 0 ? (
                                    patterns.map((pattern) => (
                                        <Card key={pattern.pattern_id}>
                                            <CardHeader>
                                                <div className="flex items-center justify-between">
                                                    <CardTitle className="text-lg capitalize">{pattern.pattern_type.replace('_', ' ')}</CardTitle>
                                                    <Badge variant="outline">{(pattern.confidence * 100).toFixed(0)}% confidence</Badge>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="space-y-4">
                                                    <div>
                                                        <p className="text-sm font-medium mb-2">{pattern.vendor} - {pattern.category}</p>
                                                        <p className="text-xs text-gray-600 dark:text-gray-400">
                                                            Frequency: {pattern.frequency} • {pattern.occurrences} occurrences
                                                        </p>
                                                    </div>
                                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                        <div>
                                                            <p className="text-gray-600 dark:text-gray-400">Typical Amount</p>
                                                            <p className="font-medium">${pattern.typical_amount?.toFixed(2)}</p>
                                                        </div>
                                                        <div>
                                                            <p className="text-gray-600 dark:text-gray-400">Last Purchase</p>
                                                            <p className="font-medium">{new Date(pattern.last_purchase).toLocaleDateString()}</p>
                                                        </div>
                                                        <div>
                                                            <p className="text-gray-600 dark:text-gray-400">Next Expected</p>
                                                            <p className="font-medium">{new Date(pattern.next_expected).toLocaleDateString()}</p>
                                                        </div>
                                                        <div>
                                                            <p className="text-gray-600 dark:text-gray-400">Typical Day</p>
                                                            <p className="font-medium">
                                                                {pattern.typical_day || pattern.typical_day_of_week || 'N/A'}
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))
                                ) : (
                                    <Card>
                                        <CardContent className="pt-6">
                                            <div className="text-center py-8">
                                                <TrendingUp className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600 mb-4" />
                                                <p className="text-sm text-gray-600 dark:text-gray-400">No patterns detected yet</p>
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

