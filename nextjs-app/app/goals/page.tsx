'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { goalsAPI, type Goal } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { Target, Plus, TrendingUp, Calendar, DollarSign, Trash2, Edit } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

export default function GoalsPage() {
    const [userId] = useState('user_123'); // TODO: Get from auth context
    const [goals, setGoals] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [selectedGoal, setSelectedGoal] = useState<any>(null);
    const [goalPlan, setGoalPlan] = useState<any>(null);
    const [goalProgress, setGoalProgress] = useState<any>(null);
    const [formData, setFormData] = useState<Partial<Goal>>({
        name: '',
        target_amount: 0,
        target_date: '',
        current_savings: 0,
        priority: 'medium',
    });
    const { toast } = useToast();

    useEffect(() => {
        loadGoals();
    }, []);

    const loadGoals = async () => {
        try {
            setLoading(true);
            const data = await goalsAPI.getGoals(userId);
            setGoals(data.goals || []);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load goals',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleCreateGoal = async () => {
        try {
            await goalsAPI.createGoal({
                user_id: userId,
                ...formData,
            } as Goal);
            toast({
                title: 'Success',
                description: 'Goal created successfully',
                variant: 'success',
            });
            setDialogOpen(false);
            setFormData({
                name: '',
                target_amount: 0,
                target_date: '',
                current_savings: 0,
                priority: 'medium',
            });
            loadGoals();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to create goal',
                variant: 'destructive',
            });
        }
    };

    const handleViewGoal = async (goalId: string) => {
        try {
            const [goal, plan, progress] = await Promise.all([
                goalsAPI.getGoal(goalId),
                goalsAPI.getGoalPlan(goalId).catch(() => null),
                goalsAPI.getGoalProgress(goalId).catch(() => null),
            ]);
            setSelectedGoal(goal);
            setGoalPlan(plan);
            setGoalProgress(progress);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load goal details',
                variant: 'destructive',
            });
        }
    };

    const handleDeleteGoal = async (goalId: string) => {
        if (!confirm('Are you sure you want to delete this goal?')) return;
        try {
            await goalsAPI.deleteGoal(goalId);
            toast({
                title: 'Success',
                description: 'Goal deleted successfully',
                variant: 'success',
            });
            loadGoals();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to delete goal',
                variant: 'destructive',
            });
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'critical':
                return 'error';
            case 'high':
                return 'warning';
            case 'medium':
                return 'default';
            default:
                return 'secondary';
        }
    };

    return (
        <Container>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-bold text-black dark:text-white">Financial Goals</h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            Set and track your financial goals
                        </p>
                    </div>
                    <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                        <DialogTrigger asChild>
                            <Button>
                                <Plus className="h-4 w-4 mr-2" />
                                New Goal
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Create New Goal</DialogTitle>
                                <DialogDescription>Set a financial goal and track your progress</DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <Label>Goal Name</Label>
                                    <Input
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        placeholder="e.g., Buy a Car"
                                    />
                                </div>
                                <div>
                                    <Label>Target Amount ($)</Label>
                                    <Input
                                        type="number"
                                        value={formData.target_amount}
                                        onChange={(e) => setFormData({ ...formData, target_amount: parseFloat(e.target.value) || 0 })}
                                    />
                                </div>
                                <div>
                                    <Label>Target Date</Label>
                                    <Input
                                        type="date"
                                        value={formData.target_date}
                                        onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <Label>Current Savings ($)</Label>
                                    <Input
                                        type="number"
                                        value={formData.current_savings}
                                        onChange={(e) => setFormData({ ...formData, current_savings: parseFloat(e.target.value) || 0 })}
                                    />
                                </div>
                                <div>
                                    <Label>Priority</Label>
                                    <select
                                        className="w-full p-2 border border-gray-200 dark:border-gray-800 rounded-md bg-white dark:bg-black text-black dark:text-white"
                                        value={formData.priority}
                                        onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                                    >
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                    </select>
                                </div>
                                <Button onClick={handleCreateGoal} className="w-full">
                                    Create Goal
                                </Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {[1, 2, 3].map((i) => (
                            <Skeleton key={i} className="h-64" />
                        ))}
                    </div>
                ) : goals.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {goals.map((goal) => (
                            <Card
                                key={goal.goal_id}
                                className="cursor-pointer hover:shadow-lg transition-shadow"
                                onClick={() => handleViewGoal(goal.goal_id)}
                            >
                                <CardHeader>
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="text-lg">{goal.name}</CardTitle>
                                        <Badge variant={getPriorityColor(goal.priority) as any}>{goal.priority}</Badge>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div>
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm text-gray-600 dark:text-gray-400">Progress</span>
                                                <span className="text-sm font-bold">{goal.progress_percentage?.toFixed(1) || 0}%</span>
                                            </div>
                                            <Progress value={goal.progress_percentage || 0} className="h-2" />
                                        </div>
                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <p className="text-gray-600 dark:text-gray-400">Target</p>
                                                <p className="font-bold">${goal.target_amount?.toFixed(2)}</p>
                                            </div>
                                            <div>
                                                <p className="text-gray-600 dark:text-gray-400">Saved</p>
                                                <p className="font-bold">${goal.current_savings?.toFixed(2)}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                            <Calendar className="h-4 w-4" />
                                            <span>{new Date(goal.target_date).toLocaleDateString()}</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Badge variant={goal.status === 'on_track' ? 'success' : goal.status === 'ahead' ? 'default' : 'warning'}>
                                                {goal.status}
                                            </Badge>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDeleteGoal(goal.goal_id);
                                                }}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                ) : (
                    <Card>
                        <CardContent className="pt-6">
                            <div className="text-center py-8">
                                <Target className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600 mb-4" />
                                <p className="text-sm text-gray-600 dark:text-gray-400">No goals yet. Create your first goal!</p>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Goal Details Dialog */}
                {selectedGoal && (
                    <Dialog open={!!selectedGoal} onOpenChange={() => setSelectedGoal(null)}>
                        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                            <DialogHeader>
                                <DialogTitle>{selectedGoal.name}</DialogTitle>
                                <DialogDescription>Goal details and plan</DialogDescription>
                            </DialogHeader>
                            <div className="space-y-6">
                                {goalPlan && (
                                    <div>
                                        <h3 className="font-semibold mb-2">Savings Plan</h3>
                                        <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                            <div className="grid grid-cols-2 gap-4 mb-4">
                                                <div>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Required</p>
                                                    <p className="text-xl font-bold">${goalPlan.plan?.monthly_savings_required?.toFixed(2)}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">Current Rate</p>
                                                    <p className="text-xl font-bold">${goalPlan.plan?.current_savings_rate?.toFixed(2)}</p>
                                                </div>
                                            </div>
                                            {goalPlan.plan?.recommendations && (
                                                <div>
                                                    <p className="text-sm font-medium mb-2">Recommendations:</p>
                                                    <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300 space-y-1">
                                                        {goalPlan.plan.recommendations.map((rec: string, i: number) => (
                                                            <li key={i}>{rec}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                                {goalProgress && (
                                    <div>
                                        <h3 className="font-semibold mb-2">Progress</h3>
                                        <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                                                {goalProgress.ahead_behind || 'On track'}
                                            </p>
                                            {goalProgress.adjustments_needed && (
                                                <div>
                                                    <p className="text-sm font-medium mb-2">Adjustments Needed:</p>
                                                    <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300 space-y-1">
                                                        {goalProgress.adjustments_needed.map((adj: string, i: number) => (
                                                            <li key={i}>{adj}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </DialogContent>
                    </Dialog>
                )}
            </div>
        </Container>
    );
}

