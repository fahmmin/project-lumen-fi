'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ingestionAPI, auditAPI } from '@/services/api';
import { pinataService } from '@/services/pinata';
import { hashJSONToBytes32, encryptAuditReport } from '@/services/crypto';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import {
    Upload,
    FileText,
    Loader2,
    CheckCircle2,
    AlertCircle,
    XCircle,
    FileSearch,
    Lock,
    Hash,
} from 'lucide-react';
import { AuditStatusBadge } from '@/components/financial/AuditStatusBadge';
import { AmountDisplay } from '@/components/financial/AmountDisplay';

type Step = 'idle' | 'uploading' | 'processing' | 'auditing' | 'hashing' | 'complete' | 'error';

export function UnifiedAuditFlow() {
    const { userId } = useUser();
    const [open, setOpen] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [step, setStep] = useState<Step>('idle');
    const [progress, setProgress] = useState('');
    const [uploadResult, setUploadResult] = useState<any>(null);
    const [auditResult, setAuditResult] = useState<any>(null);
    const [ipfsHash, setIpfsHash] = useState<string>('');
    const [dataHash, setDataHash] = useState<string>('');
    const [isDragging, setIsDragging] = useState(false);
    const { toast } = useToast();
    const router = useRouter();

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            handleFileSelect(droppedFile);
        }
    }, []);

    const handleFileSelect = (selectedFile: File) => {
        const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(selectedFile.type)) {
            toast({
                title: 'Invalid file type',
                description: 'Please upload a PDF or image file (JPEG, PNG)',
                variant: 'destructive',
            });
            return;
        }
        setFile(selectedFile);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    };

    const executeUnifiedFlow = async () => {
        if (!file) {
            toast({
                title: 'No file selected',
                description: 'Please select a file to upload',
                variant: 'destructive',
            });
            return;
        }

        try {
            // Check backend health first
            try {
                await auditAPI.healthCheck();
            } catch (healthError) {
                throw new Error(`Backend API is not accessible. Please make sure the backend is running at ${process.env.NEXT_PUBLIC_PYTHON_API_URL || 'http://localhost:8000'}`);
            }
            // Step 1: Upload to IPFS (optional - skip if Pinata not configured)
            let ipfsHashValue = '';
            try {
                setStep('uploading');
                setProgress('Uploading document to IPFS...');
                if (pinataService.isInitialized() || process.env.NEXT_PUBLIC_PINATA_API_KEY) {
                    pinataService.initialize();
                    const ipfsResult = await pinataService.uploadFile(file);
                    ipfsHashValue = ipfsResult.IpfsHash;
                    setIpfsHash(ipfsResult.IpfsHash);
                    toast({
                        title: 'Uploaded to IPFS',
                        description: `IPFS Hash: ${ipfsResult.IpfsHash.slice(0, 8)}...`,
                        variant: 'success',
                    });
                } else {
                    setProgress('Skipping IPFS upload (Pinata not configured)...');
                    toast({
                        title: 'Info',
                        description: 'IPFS upload skipped. Pinata API key not configured.',
                        variant: 'default',
                    });
                }
            } catch (ipfsError: any) {
                console.warn('IPFS upload failed, continuing without it:', ipfsError);
                toast({
                    title: 'IPFS Upload Skipped',
                    description: ipfsError.message || 'Continuing without IPFS upload',
                    variant: 'default',
                });
            }

            // Step 2: Ingest and OCR
            setStep('processing');
            setProgress('Processing document and extracting data...');
            let ingestionResult;
            try {
                ingestionResult = await ingestionAPI.uploadDocument(file);
                setUploadResult(ingestionResult);
                toast({
                    title: 'Document processed',
                    description: 'Data extracted successfully',
                    variant: 'success',
                });
            } catch (ingestError: any) {
                const errorMsg = ingestError.message || 'Failed to process document';
                console.error('Ingestion error:', ingestError);
                throw new Error(`Document processing failed: ${errorMsg}. Make sure the backend API is running at ${process.env.NEXT_PUBLIC_PYTHON_API_URL || 'http://localhost:8000'}`);
            }

            // Step 3: Run Audit
            setStep('auditing');
            setProgress('Running comprehensive AI audit...');
            const invoiceData = {
                vendor: ingestionResult.extracted_fields.vendor || '',
                date: ingestionResult.extracted_fields.date || new Date().toISOString().split('T')[0],
                amount: ingestionResult.extracted_fields.amount || 0,
                tax: ingestionResult.extracted_fields.tax || 0,
                category: ingestionResult.extracted_fields.category || '',
                invoice_number: ingestionResult.extracted_fields.invoice_number || '',
                items: ingestionResult.extracted_fields.items || [],
                payment_method: ingestionResult.extracted_fields.payment_method || '',
            };

            let audit;
            try {
                audit = await auditAPI.executeAudit(invoiceData, userId || undefined);
                setAuditResult(audit);
                toast({
                    title: 'Audit completed',
                    description: `Status: ${audit.overall_status}`,
                    variant: audit.overall_status === 'pass' ? 'success' : 'default',
                });
            } catch (auditError: any) {
                const errorMsg = auditError.message || 'Failed to run audit';
                console.error('Audit error:', auditError);
                throw new Error(`Audit failed: ${errorMsg}. Make sure the backend API is running.`);
            }

            // Step 4: Hash the audit result
            setStep('hashing');
            setProgress('Generating hash for audit report...');
            const auditData = {
                audit_id: audit.audit_id,
                timestamp: audit.timestamp,
                invoice_data: audit.invoice_data,
                findings: audit.findings,
                overall_status: audit.overall_status,
                ipfs_hash: ipfsHashValue || ipfsHash,
            };
            const hash = hashJSONToBytes32(auditData);
            setDataHash(hash);
            toast({
                title: 'Hash generated',
                description: 'Audit report hashed successfully',
                variant: 'success',
            });

            setStep('complete');
            setProgress('All steps completed successfully!');
        } catch (error: any) {
            setStep('error');
            const errorMessage = error.message || 'Failed to complete audit flow';
            setProgress(`Error: ${errorMessage}`);
            console.error('Unified audit flow error:', error);
            toast({
                title: 'Error',
                description: errorMessage,
                variant: 'destructive',
            });
        }
    };

    const resetFlow = () => {
        setFile(null);
        setStep('idle');
        setProgress('');
        setUploadResult(null);
        setAuditResult(null);
        setIpfsHash('');
        setDataHash('');
    };

    const getStepIcon = (currentStep: Step, targetStep: Step) => {
        if (currentStep === 'idle' || currentStep === 'error') return null;
        const stepOrder: Step[] = ['idle', 'uploading', 'processing', 'auditing', 'hashing', 'complete', 'error'];
        const currentIndex = stepOrder.indexOf(currentStep);
        const targetIndex = stepOrder.indexOf(targetStep);

        if (currentStep === 'complete' || (targetIndex < currentIndex && currentIndex < stepOrder.length - 1)) {
            return <CheckCircle2 className="h-5 w-5 text-black dark:text-white" />;
        }
        if (targetIndex === currentIndex) {
            return <Loader2 className="h-5 w-5 animate-spin text-black dark:text-white" />;
        }
        return <div className="h-5 w-5 rounded-full border-2 border-gray-300 dark:border-gray-700" />;
    };

    return (
        <Dialog open={open} onOpenChange={(isOpen) => {
            setOpen(isOpen);
            if (!isOpen) {
                resetFlow();
            }
        }}>
            <DialogTrigger asChild>
                <Button size="lg" className="w-full sm:w-auto">
                    <FileSearch className="h-4 w-4 mr-2" />
                    Quick Audit
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Unified Audit Flow</DialogTitle>
                    <DialogDescription>
                        Upload a document to automatically process, audit, and hash it
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6">
                    {/* File Upload */}
                    {step === 'idle' && (
                        <div
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            className={`
                border-2 border-dashed rounded-lg p-12 text-center transition-colors
                ${isDragging ? 'border-black dark:border-white bg-gray-50 dark:bg-gray-900' : 'border-gray-300 dark:border-gray-700'}
                ${file ? 'border-black dark:border-white' : ''}
              `}
                        >
                            <input
                                type="file"
                                id="unified-file-input"
                                className="hidden"
                                accept=".pdf,.jpg,.jpeg,.png"
                                onChange={handleFileInput}
                            />
                            <label htmlFor="unified-file-input" className="cursor-pointer">
                                {file ? (
                                    <div className="space-y-4">
                                        <CheckCircle2 className="h-12 w-12 mx-auto text-black dark:text-white" />
                                        <div>
                                            <p className="font-semibold text-lg">{file.name}</p>
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                {(file.size / 1024).toFixed(2)} KB
                                            </p>
                                        </div>
                                        <Button onClick={executeUnifiedFlow} className="mt-4">
                                            Start Audit Flow
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        <Upload className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600" />
                                        <div>
                                            <p className="font-semibold">Click to upload or drag and drop</p>
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                PDF, JPEG, or PNG (max 10MB)
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </label>
                        </div>
                    )}

                    {/* Progress Steps */}
                    {step !== 'idle' && (
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <div className="flex items-center gap-3">
                                    {getStepIcon(step, 'uploading')}
                                    <span className="flex-1">Upload to IPFS (Optional)</span>
                                    {ipfsHash && (
                                        <Badge variant="outline" className="text-xs font-mono">
                                            {ipfsHash.slice(0, 8)}...
                                        </Badge>
                                    )}
                                    {!ipfsHash && step !== 'uploading' && step !== 'error' && (
                                        <Badge variant="secondary" className="text-xs">
                                            Skipped
                                        </Badge>
                                    )}
                                </div>
                                <div className="flex items-center gap-3">
                                    {getStepIcon(step, 'processing')}
                                    <span className="flex-1">Process & Extract Data</span>
                                    {uploadResult && (
                                        <Badge variant="outline" className="text-xs">
                                            {uploadResult.chunks_created} chunks
                                        </Badge>
                                    )}
                                </div>
                                <div className="flex items-center gap-3">
                                    {getStepIcon(step, 'auditing')}
                                    <span className="flex-1">Run AI Audit</span>
                                    {auditResult && (
                                        <AuditStatusBadge
                                            status={auditResult.overall_status as 'pass' | 'warning' | 'error'}
                                        />
                                    )}
                                </div>
                                <div className="flex items-center gap-3">
                                    {getStepIcon(step, 'hashing')}
                                    <span className="flex-1">Generate Hash</span>
                                    {dataHash && (
                                        <Badge variant="outline" className="text-xs font-mono">
                                            {dataHash.slice(0, 8)}...
                                        </Badge>
                                    )}
                                </div>
                            </div>

                            {progress && (
                                <p className="text-sm text-gray-600 dark:text-gray-400">{progress}</p>
                            )}
                        </div>
                    )}

                    {/* Results */}
                    {step === 'complete' && auditResult && (
                        <div className="space-y-4">
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <h3 className="text-lg font-semibold">Audit Results</h3>
                                            <AuditStatusBadge
                                                status={auditResult.overall_status as 'pass' | 'warning' | 'error'}
                                            />
                                        </div>

                                        {auditResult.invoice_data?.amount && (
                                            <div>
                                                <AmountDisplay
                                                    amount={auditResult.invoice_data.amount}
                                                    size="lg"
                                                />
                                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                    {auditResult.invoice_data.vendor}
                                                </p>
                                            </div>
                                        )}

                                        {auditResult.explanation && (
                                            <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
                                                <h4 className="font-semibold mb-2">Summary</h4>
                                                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                                                    {auditResult.explanation}
                                                </p>
                                            </div>
                                        )}

                                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                                            <div>
                                                <p className="text-xs text-gray-600 dark:text-gray-400">IPFS Hash</p>
                                                <p className="text-sm font-mono break-all">{ipfsHash}</p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-gray-600 dark:text-gray-400">Data Hash</p>
                                                <p className="text-sm font-mono break-all">{dataHash}</p>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <div className="flex gap-4">
                                <Button
                                    onClick={() => {
                                        if (auditResult?.audit_id) {
                                            router.push(`/store?auditId=${auditResult.audit_id}`);
                                        } else {
                                            router.push('/store');
                                        }
                                        setOpen(false);
                                    }}
                                    className="flex-1"
                                >
                                    Store on Blockchain
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => {
                                        router.push('/insights');
                                        setOpen(false);
                                    }}
                                >
                                    View Insights
                                </Button>
                            </div>
                        </div>
                    )}

                    {step === 'error' && (
                        <Card>
                            <CardContent className="pt-6">
                                <div className="space-y-4">
                                    <div className="flex items-start gap-3">
                                        <XCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5" />
                                        <div className="flex-1">
                                            <p className="font-semibold text-red-600 dark:text-red-400 mb-2">Error</p>
                                            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{progress}</p>
                                        </div>
                                    </div>
                                    <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
                                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">Troubleshooting:</p>
                                        <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1 list-disc list-inside">
                                            <li>Make sure the backend API is running</li>
                                            <li>Check that the API URL is correct: {process.env.NEXT_PUBLIC_PYTHON_API_URL || 'http://localhost:8000'}</li>
                                            <li>Verify the file format is supported (PDF, JPEG, PNG)</li>
                                            <li>Check browser console for detailed error messages</li>
                                        </ul>
                                    </div>
                                    <Button onClick={resetFlow} className="w-full">
                                        Try Again
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}

