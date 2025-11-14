'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ingestionAPI, type IngestionResponse } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { Upload, File, CheckCircle2, ArrowRight, Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState<IngestionResponse | null>(null);
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

        if (selectedFile.size > 10 * 1024 * 1024) {
            toast({
                title: 'File too large',
                description: 'File size must be less than 10MB',
                variant: 'destructive',
            });
            return;
        }

        setFile(selectedFile);
        setUploadResult(null);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            toast({
                title: 'No file selected',
                description: 'Please select a file to upload',
                variant: 'destructive',
            });
            return;
        }

        setUploading(true);
        setUploadResult(null);

        try {
            const result = await ingestionAPI.uploadDocument(file);
            setUploadResult(result);
            toast({
                title: 'Upload successful',
                description: 'Document has been processed and indexed',
                variant: 'success',
            });
        } catch (error: any) {
            toast({
                title: 'Upload failed',
                description: error.message || 'Failed to upload document',
                variant: 'destructive',
            });
        } finally {
            setUploading(false);
        }
    };

    const handleRunAudit = () => {
        if (uploadResult?.extracted_fields) {
            const invoiceData = {
                vendor: uploadResult.extracted_fields.vendor || '',
                date: uploadResult.extracted_fields.date || new Date().toISOString().split('T')[0],
                amount: uploadResult.extracted_fields.amount || 0,
                tax: uploadResult.extracted_fields.tax || 0,
                category: uploadResult.extracted_fields.category || '',
                invoice_number: uploadResult.extracted_fields.invoice_number || '',
                items: uploadResult.extracted_fields.items || [],
                payment_method: uploadResult.extracted_fields.payment_method || '',
            };

            // Store in sessionStorage to pre-fill audit form
            sessionStorage.setItem('auditData', JSON.stringify(invoiceData));
            router.push('/audit');
        }
    };

    return (
        <Container>
            <div className="max-w-4xl mx-auto space-y-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2 text-black dark:text-white">Upload Document</h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Upload financial documents (PDF or images) for AI-powered analysis
                    </p>
                </div>

                {/* Upload Area */}
                <Card>
                    <CardHeader>
                        <CardTitle>Select Document</CardTitle>
                        <CardDescription>
                            Drag and drop a file or click to browse
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
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
                                id="file-input"
                                className="hidden"
                                accept=".pdf,.jpg,.jpeg,.png"
                                onChange={handleFileInput}
                            />
                            <label htmlFor="file-input" className="cursor-pointer">
                                {file ? (
                                    <div className="space-y-4">
                                        <CheckCircle2 className="h-12 w-12 mx-auto text-black" />
                                        <div>
                                            <p className="font-semibold text-lg">{file.name}</p>
                                            <p className="text-sm text-gray-600 mt-1">
                                                {(file.size / 1024).toFixed(2)} KB
                                            </p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        <Upload className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600" />
                                        <div>
                                            <p className="font-semibold">
                                                Click to upload or drag and drop
                                            </p>
                                            <p className="text-sm text-gray-600 mt-1">
                                                PDF, JPEG, or PNG (max 10MB)
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </label>
                        </div>

                        {file && (
                            <div className="mt-4 flex gap-4">
                                <Button
                                    onClick={handleUpload}
                                    disabled={uploading}
                                    className="flex-1"
                                >
                                    {uploading ? (
                                        <>
                                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                            Uploading...
                                        </>
                                    ) : (
                                        <>
                                            <Upload className="h-4 w-4 mr-2" />
                                            Upload & Process
                                        </>
                                    )}
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => {
                                        setFile(null);
                                        setUploadResult(null);
                                    }}
                                >
                                    Clear
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Upload Result */}
                {uploadResult && (
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <CheckCircle2 className="h-5 w-5 text-black" />
                                Document Processed
                            </CardTitle>
                            <CardDescription>
                                Document ID: {uploadResult.document_id}
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-sm text-gray-600">Filename</p>
                                    <p className="font-medium">{uploadResult.filename}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">Chunks Created</p>
                                    <p className="font-medium">{uploadResult.chunks_created}</p>
                                </div>
                            </div>

                            {/* Extracted Fields */}
                            {uploadResult.extracted_fields && (
                                <div className="border-t pt-4">
                                    <h3 className="font-semibold mb-3">Extracted Data</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        {Object.entries(uploadResult.extracted_fields)
                                            .filter(([key]) => !['document_id', 'filename', 'ingestion_timestamp'].includes(key))
                                            .map(([key, value]) => (
                                                <div key={key}>
                                                    <p className="text-sm text-gray-600 capitalize">
                                                        {key.replace(/_/g, ' ')}
                                                    </p>
                                                    <p className="font-medium">
                                                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                                    </p>
                                                </div>
                                            ))}
                                    </div>
                                </div>
                            )}

                            <div className="flex gap-4 pt-4 border-t">
                                <Button onClick={handleRunAudit} className="flex-1">
                                    Run Audit
                                    <ArrowRight className="h-4 w-4 ml-2" />
                                </Button>
                                <Link href="/documents">
                                    <Button variant="outline">View All Documents</Button>
                                </Link>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </Container>
    );
}
