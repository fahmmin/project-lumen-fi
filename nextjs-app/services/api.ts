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
    async executeAudit(invoiceData: InvoiceData): Promise<AuditResponse> {
        try {
            const response = await axios.post<AuditResponse>(
                `${API_BASE_URL}/audit/`,
                {
                    invoice_data: invoiceData,
                }
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
    async quickAudit(invoiceData: InvoiceData): Promise<any> {
        try {
            const response = await axios.post(
                `${API_BASE_URL}/audit/quick`,
                invoiceData
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
        period?: 'week' | 'month' | 'quarter' | 'year';
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

    async getGoal(goalId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/goals/${goalId}`);
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

    async getGoalPlan(goalId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/goals/${goalId}/plan`);
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

    async getGoalProgress(goalId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/goals/${goalId}/progress`);
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

    async updateGoal(goalId: string, updates: Partial<Goal>): Promise<any> {
        try {
            const response = await axios.put(`${API_BASE_URL}/goals/${goalId}`, updates);
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

    async deleteGoal(goalId: string): Promise<any> {
        try {
            const response = await axios.delete(`${API_BASE_URL}/goals/${goalId}`);
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

    async snoozePattern(patternId: string, snoozeUntil: string): Promise<any> {
        try {
            const response = await axios.post(`${API_BASE_URL}/patterns/${patternId}/snooze`, {
                snooze_until: snoozeUntil,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to snooze pattern'
                );
            }
            throw error;
        }
    },

    async dismissReminder(reminderId: string): Promise<any> {
        try {
            const response = await axios.delete(`${API_BASE_URL}/reminders/${reminderId}`);
            return response.data;
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

    async getSavings(userId: string): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/subscriptions/${userId}/savings`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(
                    error.response?.data?.detail || 'Failed to get savings'
                );
            }
            throw error;
        }
    },
};

