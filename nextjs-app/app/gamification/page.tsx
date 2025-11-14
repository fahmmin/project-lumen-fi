'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { gamificationAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { Trophy, Award, TrendingUp, Users, Star, Zap, Target, Flame, Wallet } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

export default function GamificationPage() {
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [stats, setStats] = useState<any>(null);
    const [badges, setBadges] = useState<any>(null);
    const [leaderboard, setLeaderboard] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    const loadData = async () => {
        if (!userId) return;
        setLoading(true);
        try {
            const [statsData, badgesData, leaderboardData] = await Promise.all([
                gamificationAPI.getUserStats(userId!).catch(() => null),
                gamificationAPI.getUserBadges(userId!).catch(() => null),
                gamificationAPI.getLeaderboard(20, userId!).catch(() => []),
            ]);
            setStats(statsData);
            setBadges(badgesData);
            setLeaderboard(leaderboardData);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load gamification data',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [userId]);

    const handleDailyLogin = async () => {
        if (!userId) return;
        try {
            const result = await gamificationAPI.recordDailyLogin(userId);
            if (result.already_logged_in) {
                toast({
                    title: 'Already Logged In',
                    description: result.message || 'You\'ve already logged in today. Come back tomorrow!',
                    variant: 'default',
                });
            } else {
                toast({
                    title: 'Daily Login Recorded!',
                    description: `+${result.points_earned} points! Streak: ${result.current_streak} days`,
                    variant: 'success',
                });
            }
            loadData();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to record daily login',
                variant: 'destructive',
            });
        }
    };

    const getLevelProgress = () => {
        if (!stats) return 0;
        const currentLevelPoints = (stats.level - 1) * 1000;
        const nextLevelPoints = stats.level * 1000;
        const progress = ((stats.total_points - currentLevelPoints) / (nextLevelPoints - currentLevelPoints)) * 100;
        return Math.max(0, Math.min(100, progress));
    };

    return (
        <Container>
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold mb-2">Gamification</h1>
                    <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                        Track your progress, earn badges, and compete on the leaderboard
                    </p>
                </div>

                {/* Wallet Connection */}
                {!isConnected && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Connect Wallet</CardTitle>
                            <CardDescription>Connect your wallet to view your gamification stats</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button onClick={connectWallet} className="w-full sm:w-auto">
                                <Wallet className="h-4 w-4 mr-2" />
                                Connect Wallet
                            </Button>
                        </CardContent>
                    </Card>
                )}

                {userLoading || loading ? (
                    <div className="space-y-4">
                        <Skeleton className="h-32 w-full" />
                        <Skeleton className="h-64 w-full" />
                    </div>
                ) : stats ? (
                    <>
                        {/* Stats Overview */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Trophy className="h-5 w-5" />
                                        Level {stats.level}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-3xl font-bold mb-2">{stats.total_points.toLocaleString()}</div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Total Points</p>
                                    <Progress value={getLevelProgress()} className="h-2" />
                                    <p className="text-xs text-gray-500 mt-2">
                                        {stats.total_points % 1000} / 1000 to next level
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Flame className="h-5 w-5" />
                                        Streak
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-3xl font-bold mb-2">{stats.current_streak}</div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Days</p>
                                    {stats.longest_streak > stats.current_streak && (
                                        <p className="text-xs text-gray-500 mt-2">
                                            Best: {stats.longest_streak} days
                                        </p>
                                    )}
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Award className="h-5 w-5" />
                                        Badges
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-3xl font-bold mb-2">
                                        {badges?.earned_badges?.length || 0} / {badges?.total_badges || 0}
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Earned</p>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Daily Login */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Daily Login</CardTitle>
                                <CardDescription>Check in daily to maintain your streak and earn points</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Button onClick={handleDailyLogin} className="w-full sm:w-auto">
                                    <Zap className="h-4 w-4 mr-2" />
                                    Record Daily Login
                                </Button>
                            </CardContent>
                        </Card>

                        {/* Badges */}
                        {badges && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Badges</CardTitle>
                                    <CardDescription>
                                        {badges.earned_badges?.length || 0} of {badges.total_badges || 0} badges earned
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                                        {badges.earned_badges?.map((badge: any, index: number) => (
                                            <div
                                                key={index}
                                                className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg text-center"
                                            >
                                                <Star className="h-8 w-8 mx-auto mb-2 text-yellow-500 fill-yellow-500" />
                                                <p className="font-semibold text-sm">{badge.name}</p>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    {badge.unlocked_at ? new Date(badge.unlocked_at).toLocaleDateString() : ''}
                                                </p>
                                            </div>
                                        ))}
                                        {badges.unearned_badges?.slice(0, 8).map((badge: any, index: number) => (
                                            <div
                                                key={index}
                                                className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg text-center opacity-50"
                                            >
                                                <Star className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                                                <p className="font-semibold text-sm">{badge.name}</p>
                                                <p className="text-xs text-gray-500 mt-1">{badge.requirement}</p>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Leaderboard */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Users className="h-5 w-5" />
                                    Leaderboard
                                </CardTitle>
                                <CardDescription>Top performers ranked by points</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-2">
                                    {leaderboard.map((entry, index) => (
                                        <div
                                            key={index}
                                            className={`flex items-center justify-between p-3 rounded-lg ${entry.is_current_user
                                                ? 'bg-gray-100 dark:bg-gray-900 border-2 border-black dark:border-white'
                                                : 'bg-gray-50 dark:bg-gray-950'
                                                }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-full bg-black dark:bg-white text-white dark:text-black flex items-center justify-center font-bold">
                                                    {index + 1}
                                                </div>
                                                <div>
                                                    <p className="font-semibold">{entry.display_name || entry.user_id}</p>
                                                    {entry.is_current_user && (
                                                        <Badge variant="outline" className="text-xs mt-1">
                                                            You
                                                        </Badge>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-bold">{(entry.points || 0).toLocaleString()}</p>
                                                <p className="text-xs text-gray-500">Level {entry.level || 1}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </>
                ) : !isConnected ? (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <Wallet className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                            <p className="text-gray-600 dark:text-gray-400">
                                Connect your wallet to view your gamification stats
                            </p>
                        </CardContent>
                    </Card>
                ) : !userId ? (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <p className="text-gray-600 dark:text-gray-400">
                                Loading user information...
                            </p>
                        </CardContent>
                    </Card>
                ) : null}
            </div>
        </Container>
    );
}

