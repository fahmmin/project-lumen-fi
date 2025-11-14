import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_PYTHON_API_URL || 'http://localhost:8000';

export interface InvoiceData {
    vendor: string;
    date: string;
    amount: number;
    tax?: number;
    category?: string;
    invoice_number?: string;
    items?: Array<Record<string, any>>;
    payment_method?: string;
}

export interface AuditRequest {
    invoice_data: InvoiceData;
    agents?: string[];
}

export interface AuditResponse {
    audit_id: string;
    timestamp: string;
    invoice_data: Record<string, any>;
    findings: {
        audit?: Record<string, any>;
        compliance?: Record<string, any>;
        fraud?: Record<string, any>;
    };
    explanation?: string;
    context_chunks: Array<any>;
    overall_status: string;
}

export interface IngestionResponse {
    status: string;
    document_id: string;
    filename: string;
    extracted_fields: Record<string, any>;
    chunks_created: number;
    message: string;
}

export interface MemoryResponse {
    workspace_content: string;
    last_updated: string;
    size_bytes: number;
}

export interface WorkspaceStats {
    total_lines: number;
    total_characters: number;
    size_bytes: number;
    size_kb: number;
    documents_ingested: number;
    audits_performed: number;
}

export const auditAPI = {
    /**
     * Execute a full audit on invoice data
     */
    async executeAudit(invoiceData: InvoiceData, userId?: string): Promise<AuditResponse> {
        try {
            const params = userId ? { user_id: userId } : {};
            const response = await axios.post<AuditResponse>(
                `${API_BASE_URL}/audit/`,
                {
                    invoice_data: invoiceData,
                },
                { params }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to execute audit'
                );
            }
            throw error;
        }
    },

    /**
     * Quick audit (Audit Agent only)
     */
    async quickAudit(invoiceData: InvoiceData, userId?: string): Promise<any> {
        try {
            const params = userId ? { user_id: userId } : {};
            const response = await axios.post(
                `${API_BASE_URL}/audit/quick`,
                invoiceData,
                { params }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to execute quick audit'
                );
            }
            throw error;
        }
    },

    /**
     * Get audit history
     */
    async getAuditHistory(limit: number = 10): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/audit/history`, {
                params: { limit },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to fetch audit history'
                );
            }
            throw error;
        }
    },

    /**
     * Get audit by ID
     */
    async getAuditById(auditId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/audit/${auditId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to fetch audit'
                );
            }
            throw error;
        }
    },

    /**
     * Get all audits for a user from MongoDB
     */
    async getUserAudits(userId: string, limit: number = 100): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/audit/user/${userId}/audits`, {
                params: { limit },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to fetch user audits'
                );
            }
            throw error;
        }
    },

    /**
     * Get audit statistics for a user
     */
    async getUserAuditStats(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/audit/user/${userId}/stats`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to fetch audit stats'
                );
            }
            throw error;
        }
    },

    /**
     * Health check
     */
    async healthCheck(): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/health`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error('Backend API is not available');
            }
            throw error;
        }
    },
};

export const ingestionAPI = {
    /**
     * Upload and ingest a document (PDF or image)
     */
    async uploadDocument(file: File, userId?: string): Promise<IngestionResponse> {
        try {
            const formData = new FormData();
            formData.append('file', file);
            if (userId) {
                formData.append('user_id', userId);
            }

            const response = await axios.post<IngestionResponse>(
                `${API_BASE_URL}/ingest/`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to upload document'
                );
            }
            throw error;
        }
    },

    /**
     * Get ingestion status for a document
     */
    async getIngestionStatus(documentId: string): Promise<any> {
        try {
            const response = await axios.get(
                `${API_BASE_URL}/ingest/status/${documentId}`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get ingestion status'
                );
            }
            throw error;
        }
    },
};

export const memoryAPI = {
    /**
     * Get complete workspace memory
     */
    async getWorkspaceMemory(): Promise<MemoryResponse> {
        try {
            const response = await axios.get<MemoryResponse>(
                `${API_BASE_URL}/memory/`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get workspace memory'
                );
            }
            throw error;
        }
    },

    /**
     * Get recent workspace entries
     */
    async getRecentEntries(n: number = 10): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/memory/recent`, {
                params: { n },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get recent entries'
                );
            }
            throw error;
        }
    },

    /**
     * Search workspace
     */
    async searchWorkspace(query: string): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/memory/search`, {
                query,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to search workspace'
                );
            }
            throw error;
        }
    },

    /**
     * Get workspace statistics
     */
    async getWorkspaceStats(): Promise<{ status: string; statistics: WorkspaceStats }> {
        try {
            const response = await axios.get(`${API_BASE_URL}/memory/stats`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get workspace stats'
                );
            }
            throw error;
        }
    },
};

// ==================== NEW API SERVICES ====================

// User Management
export interface UserProfile {
    user_id: string;
    name?: string;
    email?: string;
    salary_monthly?: number;
    currency?: string;
    budget_categories?: Record<string, number>;
    created_at?: string;
    updated_at?: string;
}

export const usersAPI = {
    async createOrUpdateProfile(profile: UserProfile): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/users/profile`, profile);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to create/update profile'
                );
            }
            throw error;
        }
    },

    async getProfile(userId: string): Promise<UserProfile> {
        try {
            const response = await axios.get(`${API_BASE_URL}/users/profile/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get profile'
                );
            }
            throw error;
        }
    },

    async updateProfile(userId: string, profile: Partial<UserProfile>): Promise<any> {
        try {
            const response = await axios.put(`${API_BASE_URL}/users/profile/${userId}`, profile);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to update profile'
                );
            }
            throw error;
        }
    },

    async setSalary(userId: string, salary: number, currency: string = 'USD'): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/users/${userId}/salary`, {
                salary_monthly: salary,
                currency,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to set salary'
                );
            }
            throw error;
        }
    },

    async deleteProfile(userId: string): Promise<any> {
        try {
            const response = await axios.delete(`${API_BASE_URL}/users/profile/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to delete profile'
                );
            }
            throw error;
        }
    },
};

// Personal Finance
export const financeAPI = {
    async getDashboard(userId: string, period: 'month' | 'quarter' | 'year' = 'month'): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/dashboard/${userId}`, {
                params: { period },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get dashboard'
                );
            }
            throw error;
        }
    },

    async getSpending(userId: string, params?: {
        start_date?: string;
        end_date?: string;
        category?: string;
    }): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/spending/${userId}`, {
                params,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get spending'
                );
            }
            throw error;
        }
    },

    async getPredictions(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/predictions/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get predictions'
                );
            }
            throw error;
        }
    },

    async getInsights(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/insights/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get insights'
                );
            }
            throw error;
        }
    },

    async getBudgetRecommendations(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/budget-recommendations/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get budget recommendations'
                );
            }
            throw error;
        }
    },

    async getHealthScore(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/health-score/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get health score'
                );
            }
            throw error;
        }
    },

    async getBehavior(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/behavior/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get behavior analysis'
                );
            }
            throw error;
        }
    },
};

// Goals & Planning
export interface Goal {
    goal_id?: string;
    user_id: string;
    name: string;
    target_amount: number;
    target_date: string;
    current_savings?: number;
    priority?: 'low' | 'medium' | 'high' | 'critical';
    progress_percentage?: number;
    status?: 'on_track' | 'ahead' | 'behind';
}

export const goalsAPI = {
    async createGoal(goal: Goal): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/goals/`, goal);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to create goal'
                );
            }
            throw error;
        }
    },

    async getGoals(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/goals/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get goals'
                );
            }
            throw error;
        }
    },

    async getGoal(userId: string, goalId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/goals/${userId}/${goalId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get goal'
                );
            }
            throw error;
        }
    },

    async getGoalPlan(userId: string, goalId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/${userId}/goals/${goalId}/plan`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get goal plan'
                );
            }
            throw error;
        }
    },

    async getGoalProgress(userId: string, goalId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/finance/${userId}/goals/${goalId}/progress`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get goal progress'
                );
            }
            throw error;
        }
    },

    async updateGoal(goalId: string, userId: string, updates: Partial<Goal>): Promise<any> {
        try {
            const response = await axios.put(`${API_BASE_URL}/goals/${goalId}?user_id=${userId}`, updates);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to update goal'
                );
            }
            throw error;
        }
    },

    async deleteGoal(goalId: string, userId: string): Promise<any> {
        try {
            const response = await axios.delete(`${API_BASE_URL}/goals/${goalId}?user_id=${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to delete goal'
                );
            }
            throw error;
        }
    },
};

// Reminders & Patterns
export const remindersAPI = {
    async getReminders(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/reminders/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get reminders'
                );
            }
            throw error;
        }
    },

    async getPatterns(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/patterns/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get patterns'
                );
            }
            throw error;
        }
    },

    async dismissReminder(reminderId: string): Promise<any> {
        try {
            // Note: Backend doesn't have a dismiss endpoint yet, this is a placeholder
            // The reminders are generated dynamically, so dismissing would need backend support
            throw new Error('Dismiss reminder endpoint not yet implemented in backend');
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to dismiss reminder'
                );
            }
            throw error;
        }
    },
};

// Image Forensics
export const forensicsAPI = {
    async analyzeImage(file: File): Promise<any> {
        try {
            const formData = new FormData();
            formData.append('image', file);

            const response = await axios.post(`${API_BASE_URL}/forensics/analyze`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to analyze image'
                );
            }
            throw error;
        }
    },
};

// Subscriptions
export const subscriptionsAPI = {
    async getSubscriptions(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/subscriptions/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get subscriptions'
                );
            }
            throw error;
        }
    },

    async getUnusedSubscriptions(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/subscriptions/${userId}/unused`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get unused subscriptions'
                );
            }
            throw error;
        }
    },

    // Note: getSavings endpoint doesn't exist in backend
    // Use getUnusedSubscriptions instead which includes total_potential_savings
};

// Gamification API
export const gamificationAPI = {
    async awardPoints(userId: string, activity: string, metadata?: any): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/gamification/points/award`, {
                user_id: userId,
                activity,
                metadata,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to award points'
                );
            }
            throw error;
        }
    },

    async getUserStats(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/gamification/stats/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get user stats'
                );
            }
            throw error;
        }
    },

    async getLeaderboard(limit: number = 10, userId?: string): Promise<any[]> {
        try {
            const params = new URLSearchParams({ limit: limit.toString() });
            if (userId) params.append('user_id', userId);
            const response = await axios.get(`${API_BASE_URL}/gamification/leaderboard?${params}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get leaderboard'
                );
            }
            throw error;
        }
    },

    async getUserBadges(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/gamification/badges/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get badges'
                );
            }
            throw error;
        }
    },

    async recordDailyLogin(userId: string): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/gamification/daily-login/${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to record daily login'
                );
            }
            throw error;
        }
    },
};

// Family API
export const familyAPI = {
    async createFamily(data: { name: string; description?: string; created_by: string; shared_budget?: Record<string, number> }): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/family/create`, data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to create family'
                );
            }
            throw error;
        }
    },

    async joinFamily(inviteCode: string, userId: string, displayName?: string): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/family/join`, {
                invite_code: inviteCode,
                user_id: userId,
                display_name: displayName,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to join family'
                );
            }
            throw error;
        }
    },

    async getFamily(familyId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/family/${familyId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get family'
                );
            }
            throw error;
        }
    },

    async getUserFamilies(userId: string): Promise<any[]> {
        try {
            const response = await axios.get(`${API_BASE_URL}/family/user/${userId}/families`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get user families'
                );
            }
            throw error;
        }
    },

    async getFamilyDashboard(familyId: string, period: string = 'month'): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/family/${familyId}/dashboard?period=${period}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get family dashboard'
                );
            }
            throw error;
        }
    },

    async getMemberComparison(familyId: string, userId: string, period: string = 'month'): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/family/${familyId}/member/${userId}/comparison?period=${period}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get member comparison'
                );
            }
            throw error;
        }
    },

    async updateFamily(familyId: string, userId: string, updates: any): Promise<any> {
        try {
            const response = await axios.put(`${API_BASE_URL}/family/${familyId}/update?user_id=${userId}`, updates);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to update family'
                );
            }
            throw error;
        }
    },

    async leaveFamily(familyId: string, userId: string): Promise<any> {
        try {
            const response = await axios.delete(`${API_BASE_URL}/family/${familyId}/leave?user_id=${userId}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to leave family'
                );
            }
            throw error;
        }
    },

    async verifyInviteCode(inviteCode: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/family/invite-code/${inviteCode}/verify`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Invalid invite code'
                );
            }
            throw error;
        }
    },
};

// Social Comparison API
export const socialAPI = {
    async getUserPercentile(userId: string, period: string = 'month'): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/social/${userId}/percentile?period=${period}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get user percentile'
                );
            }
            throw error;
        }
    },

    async getCategoryLeaderboard(category: string, period: string = 'month', limit: number = 10): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/social/category/${category}/leaderboard?period=${period}&limit=${limit}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get category leaderboard'
                );
            }
            throw error;
        }
    },

    async getSocialInsights(userId: string, period: string = 'month'): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/social/insights/${userId}?period=${period}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get social insights'
                );
            }
            throw error;
        }
    },
};

// Reports API
export const reportsAPI = {
    async generateReport(userId: string, reportType: string = 'monthly_summary', period: string = 'month'): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/reports/generate/${userId}?report_type=${reportType}&period=${period}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to generate report'
                );
            }
            throw error;
        }
    },

    async downloadReport(filename: string): Promise<Blob> {
        try {
            const response = await axios.get(`${API_BASE_URL}/reports/download/${filename}`, {
                responseType: 'blob',
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to download report'
                );
            }
            throw error;
        }
    },

    async getReportHistory(userId: string, limit: number = 10): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/reports/${userId}/history?limit=${limit}`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get report history'
                );
            }
            throw error;
        }
    },
};

// Voice API
export const voiceAPI = {
    async transcribeAudio(audioFile: File): Promise<any> {
        try {
            const formData = new FormData();
            formData.append('audio', audioFile);
            const response = await axios.post(`${API_BASE_URL}/voice/transcribe`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to transcribe audio'
                );
            }
            throw error;
        }
    },

    async uploadReceiptByVoice(audioFile: File, userId: string): Promise<any> {
        try {
            const formData = new FormData();
            formData.append('audio', audioFile);
            formData.append('user_id', userId);
            const response = await axios.post(`${API_BASE_URL}/voice/upload-receipt`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to upload receipt by voice'
                );
            }
            throw error;
        }
    },

    async getSupportedFormats(): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/voice/supported-formats`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get supported formats'
                );
            }
            throw error;
        }
    },
};

// Email API
export const emailAPI = {
    async parseReceipt(userId: string, emailSubject: string, emailBody: string, senderEmail?: string): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/email/parse-receipt`, {
                user_id: userId,
                email_subject: emailSubject,
                email_body: emailBody,
                sender_email: senderEmail,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to parse email receipt'
                );
            }
            throw error;
        }
    },

    async testParser(emailSubject: string, emailBody: string): Promise<any> {
        try {
            // Backend uses Body(...) which accepts JSON
            const response = await axios.post(`${API_BASE_URL}/email/test-parser`, {
                email_subject: emailSubject,
                email_body: emailBody,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to test parser'
                );
            }
            throw error;
        }
    },

    async getExampleEmail(): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/email/example`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get example email'
                );
            }
            throw error;
        }
    },
};

