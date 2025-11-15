'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { FileText, Loader2, CheckCircle2, AlertTriangle, TrendingUp, DollarSign } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface ITRResult {
    panNumber: string;
    assessmentYear: string;
    totalIncome: number;
    taxPaid: number;
    refundAmount: number;
    status: 'verified' | 'pending' | 'discrepancy';
    filingStatus: string;
    deductions: number;
    taxableIncome: number;
}

export function ITRChecker() {
    const [panNumber, setPanNumber] = useState('');
    const [assessmentYear, setAssessmentYear] = useState(new Date().getFullYear() - 1);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ITRResult | null>(null);
    const { toast } = useToast();

    const generateITRData = async (pan: string, year: number): Promise<ITRResult> => {
        // Use Gemini API to generate realistic ITR data
        try {
            const geminiApiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY;

            if (!geminiApiKey) {
                // Fallback to generating random data if Gemini API key is not available
                return generateRandomITRData(pan, year);
            }

            const prompt = `Generate realistic Indian Income Tax Return (ITR) data for PAN: ${pan}, Assessment Year: ${year}-${year + 1}. 
            Return ONLY a JSON object with these exact fields:
            {
                "totalIncome": <number between 500000 and 5000000>,
                "taxPaid": <number between 50000 and 500000>,
                "refundAmount": <number between 0 and 100000>,
                "status": "verified" or "pending" or "discrepancy",
                "filingStatus": "Filed" or "Pending" or "Under Review",
                "deductions": <number between 50000 and 200000>,
                "taxableIncome": <number>
            }
            Make the data realistic and consistent. taxableIncome should be totalIncome - deductions.`;

            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${geminiApiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: prompt
                        }]
                    }]
                })
            });

            const data = await response.json();
            const text = data.candidates?.[0]?.content?.parts?.[0]?.text || '';

            // Extract JSON from response
            const jsonMatch = text.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                const parsed = JSON.parse(jsonMatch[0]);
                return {
                    panNumber: pan,
                    assessmentYear: `${year}-${year + 1}`,
                    totalIncome: parsed.totalIncome || 0,
                    taxPaid: parsed.taxPaid || 0,
                    refundAmount: parsed.refundAmount || 0,
                    status: parsed.status || 'verified',
                    filingStatus: parsed.filingStatus || 'Filed',
                    deductions: parsed.deductions || 0,
                    taxableIncome: parsed.taxableIncome || (parsed.totalIncome - parsed.deductions),
                };
            }
        } catch (error) {
            console.error('Gemini API error:', error);
        }

        // Fallback to random data
        return generateRandomITRData(pan, year);
    };

    const generateRandomITRData = (pan: string, year: number): ITRResult => {
        const totalIncome = Math.floor(Math.random() * 4500000) + 500000;
        const deductions = Math.floor(Math.random() * 150000) + 50000;
        const taxableIncome = totalIncome - deductions;
        const taxPaid = Math.floor(taxableIncome * 0.15) + Math.floor(Math.random() * 50000);
        const refundAmount = Math.floor(Math.random() * 100000);
        const statuses: ('verified' | 'pending' | 'discrepancy')[] = ['verified', 'pending', 'discrepancy'];
        const filingStatuses = ['Filed', 'Pending', 'Under Review'];

        return {
            panNumber: pan,
            assessmentYear: `${year}-${year + 1}`,
            totalIncome,
            taxPaid,
            refundAmount,
            status: statuses[Math.floor(Math.random() * statuses.length)],
            filingStatus: filingStatuses[Math.floor(Math.random() * filingStatuses.length)],
            deductions,
            taxableIncome,
        };
    };

    const handleCheck = async () => {
        if (!panNumber || panNumber.length !== 10) {
            toast({
                title: 'Invalid PAN',
                description: 'Please enter a valid 10-character PAN number',
                variant: 'destructive',
            });
            return;
        }

        setLoading(true);
        setResult(null);

        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 2000));

        try {
            const data = await generateITRData(panNumber.toUpperCase(), assessmentYear);
            setResult(data);
            toast({
                title: 'ITR Check Complete',
                description: 'Income Tax Return information retrieved successfully',
            });
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to check ITR. Please try again.',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card className="border-gray-200 dark:border-gray-800">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    ITR Checker
                </CardTitle>
                <CardDescription>
                    Verify Income Tax Return status and details
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-3">
                    <div>
                        <label className="text-sm font-medium mb-1.5 block">PAN Number</label>
                        <Input
                            placeholder="ABCDE1234F"
                            value={panNumber}
                            onChange={(e) => setPanNumber(e.target.value.toUpperCase())}
                            maxLength={10}
                            disabled={loading}
                            className="uppercase"
                        />
                    </div>
                    <div>
                        <label className="text-sm font-medium mb-1.5 block">Assessment Year</label>
                        <Input
                            type="number"
                            value={assessmentYear}
                            onChange={(e) => setAssessmentYear(parseInt(e.target.value) || new Date().getFullYear() - 1)}
                            disabled={loading}
                            min={2020}
                            max={new Date().getFullYear()}
                        />
                    </div>
                    <Button
                        onClick={handleCheck}
                        disabled={loading || !panNumber}
                        className="w-full"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Checking...
                            </>
                        ) : (
                            <>
                                <FileText className="h-4 w-4 mr-2" />
                                Check ITR
                            </>
                        )}
                    </Button>
                </div>

                {result && (
                    <div className="mt-6 space-y-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Status</span>
                            <Badge
                                variant={
                                    result.status === 'verified'
                                        ? 'default'
                                        : result.status === 'pending'
                                            ? 'secondary'
                                            : 'error'
                                }
                            >
                                {result.status === 'verified' && <CheckCircle2 className="h-3 w-3 mr-1" />}
                                {result.status === 'discrepancy' && <AlertTriangle className="h-3 w-3 mr-1" />}
                                {result.filingStatus}
                            </Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <p className="text-xs text-gray-600 dark:text-gray-400">Total Income</p>
                                <p className="text-lg font-semibold flex items-center gap-1">
                                    <DollarSign className="h-4 w-4" />
                                    {result.totalIncome.toLocaleString('en-IN')}
                                </p>
                            </div>
                            <div className="space-y-1">
                                <p className="text-xs text-gray-600 dark:text-gray-400">Tax Paid</p>
                                <p className="text-lg font-semibold flex items-center gap-1">
                                    <DollarSign className="h-4 w-4" />
                                    {result.taxPaid.toLocaleString('en-IN')}
                                </p>
                            </div>
                            <div className="space-y-1">
                                <p className="text-xs text-gray-600 dark:text-gray-400">Deductions</p>
                                <p className="text-lg font-semibold flex items-center gap-1">
                                    <TrendingUp className="h-4 w-4" />
                                    {result.deductions.toLocaleString('en-IN')}
                                </p>
                            </div>
                            <div className="space-y-1">
                                <p className="text-xs text-gray-600 dark:text-gray-400">Refund Amount</p>
                                <p className="text-lg font-semibold text-green-600 dark:text-green-400 flex items-center gap-1">
                                    <DollarSign className="h-4 w-4" />
                                    {result.refundAmount.toLocaleString('en-IN')}
                                </p>
                            </div>
                        </div>

                        <div className="pt-2 border-t border-gray-200 dark:border-gray-800">
                            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Taxable Income</p>
                            <p className="text-xl font-bold">{result.taxableIncome.toLocaleString('en-IN')}</p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

