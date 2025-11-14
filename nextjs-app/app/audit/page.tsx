'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AuditStatusBadge } from '@/components/financial/AuditStatusBadge';
import { InsightCard } from '@/components/financial/InsightCard';
import { AmountDisplay } from '@/components/financial/AmountDisplay';
import { auditAPI, type InvoiceData, type AuditResponse } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, CheckCircle2, AlertCircle, XCircle, ArrowRight, Database } from 'lucide-react';
import Link from 'next/link';

type AuditType = 'full' | 'quick';
type AuditStep = 'idle' | 'audit' | 'compliance' | 'fraud' | 'explainability' | 'complete';

export default function AuditPage() {
    const [formData, setFormData] = useState<InvoiceData>({
        vendor: '',
        date: new Date().toISOString().split('T')[0],
        amount: 0,
        tax: 0,
        category: '',
        invoice_number: '',
        items: [],
        payment_method: '',
    });
    const [auditType, setAuditType] = useState<AuditType>('full');
    const [loading, setLoading] = useState(false);
    const [currentStep, setCurrentStep] = useState<AuditStep>('idle');
    const [auditResult, setAuditResult] = useState<AuditResponse | null>(null);
    const { toast } = useToast();
    const router = useRouter();

    useEffect(() => {
        // Check if there's pre-filled data from upload page
        const storedData = sessionStorage.getItem('auditData');
        if (storedData) {
            try {
                const data = JSON.parse(storedData);
                setFormData(data);
                sessionStorage.removeItem('auditData');
            } catch (e) {
                // Ignore
            }
        }
    }, []);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: name === 'amount' || name === 'tax' ? parseFloat(value) || 0 : value,
        }));
    };

    const simulateProgress = async () => {
        if (auditType === 'full') {
            setCurrentStep('audit');
            await new Promise((resolve) => setTimeout(resolve, 1000));
            setCurrentStep('compliance');
            await new Promise((resolve) => setTimeout(resolve, 1000));
            setCurrentStep('fraud');
            await new Promise((resolve) => setTimeout(resolve, 1000));
            setCurrentStep('explainability');
            await new Promise((resolve) => setTimeout(resolve, 1000));
        }
        setCurrentStep('complete');
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setCurrentStep('idle');
        setAuditResult(null);

        try {
            await simulateProgress();

            const result = auditType === 'full'
                ? await auditAPI.executeAudit(formData)
                : await auditAPI.quickAudit(formData);

            setAuditResult(result as AuditResponse);
            toast({
                title: 'Audit completed',
                description: `Audit ${result.audit_id} completed successfully`,
                variant: 'success',
            });
        } catch (error: any) {
            toast({
                title: 'Audit failed',
                description: error.message || 'Failed to execute audit',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
            setCurrentStep('idle');
        }
    };

    const getStepIcon = (step: AuditStep, targetStep: AuditStep) => {
        if (currentStep === 'idle' || currentStep === 'complete') {
            return null;
        }
        if (step === targetStep) {
            return <Loader2 className="h-4 w-4 animate-spin" />;
        }
        const stepOrder: AuditStep[] = ['idle', 'audit', 'compliance', 'fraud', 'explainability', 'complete'];
        const currentIndex = stepOrder.indexOf(currentStep);
        const targetIndex = stepOrder.indexOf(targetStep);
        if (targetIndex < currentIndex) {
            return <CheckCircle2 className="h-4 w-4 text-black" />;
        }
        return null;
    };

    return (
        <Container>
            <div className="max-w-7xl mx-auto space-y-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Run Audit</h1>
                    <p className="text-gray-600">
                        Execute comprehensive AI-powered audits on invoice data
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Form Section */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Invoice Data</CardTitle>
                            <CardDescription>
                                Enter invoice details or select from uploaded documents
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                {/* Audit Type Selection */}
                                <div className="flex gap-2 mb-4">
                                    <Button
                                        type="button"
                                        variant={auditType === 'full' ? 'default' : 'outline'}
                                        onClick={() => setAuditType('full')}
                                        className="flex-1"
                                    >
                                        Full Audit
                                    </Button>
                                    <Button
                                        type="button"
                                        variant={auditType === 'quick' ? 'default' : 'outline'}
                                        onClick={() => setAuditType('quick')}
                                        className="flex-1"
                                    >
                                        Quick Audit
                                    </Button>
                                </div>

                                <div>
                                    <label htmlFor="vendor" className="block text-sm font-medium mb-1">
                                        Vendor *
                                    </label>
                                    <Input
                                        id="vendor"
                                        name="vendor"
                                        value={formData.vendor}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>

                                <div>
                                    <label htmlFor="date" className="block text-sm font-medium mb-1">
                                        Date *
                                    </label>
                                    <Input
                                        type="date"
                                        id="date"
                                        name="date"
                                        value={formData.date}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label htmlFor="amount" className="block text-sm font-medium mb-1">
                                            Amount *
                                        </label>
                                        <Input
                                            type="number"
                                            id="amount"
                                            name="amount"
                                            value={formData.amount}
                                            onChange={handleInputChange}
                                            required
                                            step="0.01"
                                        />
                                    </div>
                                    <div>
                                        <label htmlFor="tax" className="block text-sm font-medium mb-1">
                                            Tax
                                        </label>
                                        <Input
                                            type="number"
                                            id="tax"
                                            name="tax"
                                            value={formData.tax}
                                            onChange={handleInputChange}
                                            step="0.01"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label htmlFor="category" className="block text-sm font-medium mb-1">
                                        Category
                                    </label>
                                    <Input
                                        id="category"
                                        name="category"
                                        value={formData.category}
                                        onChange={handleInputChange}
                                        placeholder="e.g., Office Supplies"
                                    />
                                </div>

                                <div>
                                    <label htmlFor="invoice_number" className="block text-sm font-medium mb-1">
                                        Invoice Number
                                    </label>
                                    <Input
                                        id="invoice_number"
                                        name="invoice_number"
                                        value={formData.invoice_number}
                                        onChange={handleInputChange}
                                    />
                                </div>

                                <div>
                                    <label htmlFor="payment_method" className="block text-sm font-medium mb-1">
                                        Payment Method
                                    </label>
                                    <Input
                                        id="payment_method"
                                        name="payment_method"
                                        value={formData.payment_method}
                                        onChange={handleInputChange}
                                    />
                                </div>

                                <Button type="submit" disabled={loading} className="w-full">
                                    {loading ? (
                                        <>
                                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                            Running Audit...
                                        </>
                                    ) : (
                                        `Run ${auditType === 'full' ? 'Full' : 'Quick'} Audit`
                                    )}
                                </Button>
                            </form>

                            {/* Progress Indicator */}
                            {loading && auditType === 'full' && (
                                <div className="mt-6 space-y-2">
                                    <p className="text-sm font-medium mb-3">Audit Progress</p>
                                    {['audit', 'compliance', 'fraud', 'explainability'].map((step) => (
                                        <div key={step} className="flex items-center gap-2 text-sm">
                                            {getStepIcon(currentStep, step as AuditStep)}
                                            <span className="capitalize">{step} Agent</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Results Section */}
                    <div className="space-y-6">
                        {auditResult && (
                            <>
                                {/* Status Card */}
                                <Card>
                                    <CardHeader>
                                        <div className="flex items-center justify-between">
                                            <CardTitle>Audit Results</CardTitle>
                                            <AuditStatusBadge
                                                status={auditResult.overall_status as 'pass' | 'warning' | 'error'}
                                            />
                                        </div>
                                        <CardDescription>
                                            Audit ID: {auditResult.audit_id}
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div>
                                            <AmountDisplay
                                                amount={auditResult.invoice_data?.amount || 0}
                                                size="lg"
                                            />
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                {auditResult.invoice_data?.vendor}
                                            </p>
                                        </div>

                                        {auditResult.explanation && (
                                            <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
                                                <h3 className="font-semibold mb-2">Summary</h3>
                                                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                                                    {auditResult.explanation}
                                                </p>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>

                                {/* Findings */}
                                <Card>
                                    <CardHeader>
                                        <CardTitle>Findings</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <Tabs defaultValue="audit" className="w-full">
                                            <TabsList className="grid w-full grid-cols-3">
                                                <TabsTrigger value="audit">Audit</TabsTrigger>
                                                <TabsTrigger value="compliance">Compliance</TabsTrigger>
                                                <TabsTrigger value="fraud">Fraud</TabsTrigger>
                                            </TabsList>
                                            <TabsContent value="audit" className="mt-4">
                                                <pre className="text-xs bg-gray-50 dark:bg-gray-900 p-4 rounded overflow-auto max-h-64 text-gray-900 dark:text-gray-100">
                                                    {JSON.stringify(auditResult.findings.audit || {}, null, 2)}
                                                </pre>
                                            </TabsContent>
                                            <TabsContent value="compliance" className="mt-4">
                                                <pre className="text-xs bg-gray-50 dark:bg-gray-900 p-4 rounded overflow-auto max-h-64 text-gray-900 dark:text-gray-100">
                                                    {JSON.stringify(auditResult.findings.compliance || {}, null, 2)}
                                                </pre>
                                            </TabsContent>
                                            <TabsContent value="fraud" className="mt-4">
                                                <pre className="text-xs bg-gray-50 dark:bg-gray-900 p-4 rounded overflow-auto max-h-64 text-gray-900 dark:text-gray-100">
                                                    {JSON.stringify(auditResult.findings.fraud || {}, null, 2)}
                                                </pre>
                                            </TabsContent>
                                        </Tabs>
                                    </CardContent>
                                </Card>

                                {/* Actions */}
                                <div className="flex gap-4">
                                    <Link href="/store" className="flex-1">
                                        <Button className="w-full">
                                            Store on Blockchain
                                            <ArrowRight className="h-4 w-4 ml-2" />
                                        </Button>
                                    </Link>
                                    <Link href="/insights">
                                        <Button variant="outline">View Insights</Button>
                                    </Link>
                                </div>
                            </>
                        )}

                        {!auditResult && !loading && (
                            <Card>
                                <CardContent className="py-12 text-center">
                                    <p className="text-gray-600">
                                        Fill out the form and click "Run Audit" to see results here
                                    </p>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </Container>
    );
}
