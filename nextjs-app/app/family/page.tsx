'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { familyAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { Users, Plus, UserPlus, Copy, TrendingUp, DollarSign, BarChart3, Wallet } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

export default function FamilyPage() {
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [families, setFamilies] = useState<any[]>([]);
    const [selectedFamily, setSelectedFamily] = useState<any>(null);
    const [dashboard, setDashboard] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [createOpen, setCreateOpen] = useState(false);
    const [joinOpen, setJoinOpen] = useState(false);
    const [inviteCode, setInviteCode] = useState('');
    const [familyName, setFamilyName] = useState('');
    const [familyDescription, setFamilyDescription] = useState('');
    const [sharedBudget, setSharedBudget] = useState('');
    const { toast } = useToast();

    const loadFamilies = async () => {
        if (!userId) return;
        setLoading(true);
        try {
            const data = await familyAPI.getUserFamilies(userId);
            setFamilies(data);
            if (data.length > 0 && !selectedFamily) {
                setSelectedFamily(data[0]);
                loadDashboard(data[0].family_id);
            }
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load families',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const loadDashboard = async (familyId: string) => {
        try {
            const data = await familyAPI.getFamilyDashboard(familyId, 'month');
            setDashboard(data);
        } catch (error: any) {
            console.error('Failed to load dashboard:', error);
        }
    };

    useEffect(() => {
        loadFamilies();
    }, [userId]);

    useEffect(() => {
        if (selectedFamily) {
            loadDashboard(selectedFamily.family_id);
        }
    }, [selectedFamily]);

    const handleCreateFamily = async () => {
        if (!userId) {
            toast({
                title: 'Error',
                description: 'Please connect your wallet first',
                variant: 'destructive',
            });
            return;
        }
        if (!familyName.trim()) {
            toast({
                title: 'Error',
                description: 'Family name is required',
                variant: 'destructive',
            });
            return;
        }
        try {
            const data = await familyAPI.createFamily({
                name: familyName.trim(),
                description: familyDescription.trim() || undefined,
                created_by: userId,
                shared_budget: sharedBudget ? { 'total': parseFloat(sharedBudget) } : undefined,
            });
            toast({
                title: 'Family Created!',
                description: `Invite code: ${data.invite_code}`,
                variant: 'success',
            });
            setCreateOpen(false);
            setFamilyName('');
            setFamilyDescription('');
            setSharedBudget('');
            loadFamilies();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to create family',
                variant: 'destructive',
            });
        }
    };

    const handleJoinFamily = async () => {
        if (!userId) {
            toast({
                title: 'Error',
                description: 'Please connect your wallet first',
                variant: 'destructive',
            });
            return;
        }
        try {
            const data = await familyAPI.joinFamily(inviteCode, userId);
            toast({
                title: 'Joined Family!',
                description: `Successfully joined ${data.name}`,
                variant: 'success',
            });
            setJoinOpen(false);
            setInviteCode('');
            loadFamilies();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to join family',
                variant: 'destructive',
            });
        }
    };

    const copyInviteCode = (code: string) => {
        navigator.clipboard.writeText(code);
        toast({
            title: 'Copied!',
            description: 'Invite code copied to clipboard',
            variant: 'success',
        });
    };

    return (
        <Container>
            <div className="space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div>
                        <h1 className="text-2xl sm:text-3xl font-bold mb-2">Family & Shared Budgets</h1>
                        <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                            Create or join family groups to track shared expenses
                        </p>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-2">
                        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                            <DialogTrigger asChild>
                                <Button>
                                    <Plus className="h-4 w-4 mr-2" />
                                    Create Family
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Create New Family</DialogTitle>
                                    <DialogDescription>
                                        Create a family group and invite members with a unique code
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4">
                                    <Input
                                        placeholder="Family Name"
                                        value={familyName}
                                        onChange={(e) => setFamilyName(e.target.value)}
                                    />
                                    <Textarea
                                        placeholder="Description (optional)"
                                        value={familyDescription}
                                        onChange={(e) => setFamilyDescription(e.target.value)}
                                    />
                                    <Input
                                        type="number"
                                        placeholder="Shared Budget (optional)"
                                        value={sharedBudget}
                                        onChange={(e) => setSharedBudget(e.target.value)}
                                    />
                                    {!isConnected && (
                                        <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-sm text-yellow-800 dark:text-yellow-200">
                                            Please connect your wallet first
                                        </div>
                                    )}
                                    <Button
                                        onClick={handleCreateFamily}
                                        className="w-full"
                                        disabled={!isConnected || !userId}
                                    >
                                        Create Family
                                    </Button>
                                </div>
                            </DialogContent>
                        </Dialog>

                        <Dialog open={joinOpen} onOpenChange={setJoinOpen}>
                            <DialogTrigger asChild>
                                <Button variant="outline">
                                    <UserPlus className="h-4 w-4 mr-2" />
                                    Join Family
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Join Family</DialogTitle>
                                    <DialogDescription>
                                        Enter the 6-character invite code to join a family
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4">
                                    <Input
                                        placeholder="Invite Code (6 characters)"
                                        value={inviteCode}
                                        onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                                        maxLength={6}
                                    />
                                    {!isConnected && (
                                        <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-sm text-yellow-800 dark:text-yellow-200">
                                            Please connect your wallet first
                                        </div>
                                    )}
                                    <Button
                                        onClick={handleJoinFamily}
                                        className="w-full"
                                        disabled={!isConnected || !userId}
                                    >
                                        Join Family
                                    </Button>
                                </div>
                            </DialogContent>
                        </Dialog>
                    </div>
                </div>

                {!isConnected ? (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <Wallet className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                            <p className="text-gray-600 dark:text-gray-400 mb-4">
                                Connect your wallet to create or join a family
                            </p>
                            <Button onClick={connectWallet}>
                                <Wallet className="h-4 w-4 mr-2" />
                                Connect Wallet
                            </Button>
                        </CardContent>
                    </Card>
                ) : userLoading || loading ? (
                    <Skeleton className="h-64 w-full" />
                ) : families.length > 0 ? (
                    <Tabs defaultValue="dashboard" className="space-y-4">
                        <TabsList>
                            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                            <TabsTrigger value="families">My Families</TabsTrigger>
                        </TabsList>

                        <TabsContent value="dashboard" className="space-y-4">
                            {selectedFamily && dashboard && (
                                <>
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>{selectedFamily.name}</CardTitle>
                                            <CardDescription>
                                                Invite Code: {selectedFamily.invite_code}
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="ml-2"
                                                    onClick={() => copyInviteCode(selectedFamily.invite_code)}
                                                >
                                                    <Copy className="h-3 w-3" />
                                                </Button>
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                <div>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Spending</p>
                                                    <p className="text-2xl font-bold">
                                                        ${(dashboard.summary?.total_family_spending || 0).toLocaleString()}
                                                    </p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">Members</p>
                                                    <p className="text-2xl font-bold">{dashboard.member_count || selectedFamily.members?.length || 0}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">Budget</p>
                                                    <p className="text-2xl font-bold">
                                                        {selectedFamily.shared_budget
                                                            ? `$${(Object.values(selectedFamily.shared_budget) as number[]).reduce((sum, val) => sum + val, 0).toLocaleString()}`
                                                            : 'N/A'}
                                                    </p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">Remaining</p>
                                                    <p className="text-2xl font-bold">
                                                        {selectedFamily.shared_budget
                                                            ? `$${((Object.values(selectedFamily.shared_budget) as number[]).reduce((sum, val) => sum + val, 0) - (dashboard.summary?.total_family_spending || 0)).toLocaleString()}`
                                                            : 'N/A'}
                                                    </p>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>Spending by Member</CardTitle>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="space-y-2">
                                                    {dashboard.spending_by_member && dashboard.spending_by_member.length > 0 ? (
                                                        dashboard.spending_by_member.map((member: any, index: number) => (
                                                            <div key={index} className="flex justify-between items-center">
                                                                <span>{member.display_name || member.user_id}</span>
                                                                <span className="font-bold">${(member.total_spent || 0).toLocaleString()}</span>
                                                            </div>
                                                        ))
                                                    ) : (
                                                        <p className="text-sm text-gray-500">No member spending data available</p>
                                                    )}
                                                </div>
                                            </CardContent>
                                        </Card>

                                        <Card>
                                            <CardHeader>
                                                <CardTitle>Spending by Category</CardTitle>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="space-y-2">
                                                    {dashboard.spending_by_category && Object.keys(dashboard.spending_by_category).length > 0 ? (
                                                        Object.entries(dashboard.spending_by_category)
                                                            .sort(([, a], [, b]) => (b as number) - (a as number))
                                                            .slice(0, 5)
                                                            .map(([category, amount], index) => (
                                                                <div key={index} className="flex justify-between items-center">
                                                                    <span className="capitalize">{category}</span>
                                                                    <span className="font-bold">${(amount as number).toLocaleString()}</span>
                                                                </div>
                                                            ))
                                                    ) : (
                                                        <p className="text-sm text-gray-500">No category data available</p>
                                                    )}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    </div>
                                </>
                            )}
                        </TabsContent>

                        <TabsContent value="families" className="space-y-4">
                            {families.map((family) => (
                                <Card key={family.family_id}>
                                    <CardHeader>
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <CardTitle>{family.name}</CardTitle>
                                                <CardDescription>
                                                    {family.members?.length || 0} members • Created{' '}
                                                    {family.created_at
                                                        ? new Date(typeof family.created_at === 'string' ? family.created_at : family.created_at).toLocaleDateString()
                                                        : 'N/A'}
                                                </CardDescription>
                                            </div>
                                            <Button
                                                variant={selectedFamily?.family_id === family.family_id ? 'default' : 'outline'}
                                                onClick={() => setSelectedFamily(family)}
                                            >
                                                View
                                            </Button>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-2">
                                            <p className="text-sm">
                                                <strong>Invite Code:</strong> {family.invite_code}
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="ml-2"
                                                    onClick={() => copyInviteCode(family.invite_code)}
                                                >
                                                    <Copy className="h-3 w-3" />
                                                </Button>
                                            </p>
                                            <div className="flex flex-wrap gap-2">
                                                {family.members?.map((member: any, index: number) => (
                                                    <Badge key={index} variant="outline">
                                                        {member.display_name || member.user_id}
                                                        {member.role === 'admin' && ' (Admin)'}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </TabsContent>
                    </Tabs>
                ) : (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <Users className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                            <p className="text-gray-600 dark:text-gray-400 mb-4">
                                You're not part of any family yet. Create or join one to get started!
                            </p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </Container>
    );
}

