'use client';

import { useState } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { forensicsAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { Upload, CheckCircle2, XCircle, AlertTriangle, FileImage } from 'lucide-react';

export default function ForensicsPage() {
    const [file, setFile] = useState<File | null>(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState<any>(null);
    const { toast } = useToast();

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            if (selectedFile.type.startsWith('image/')) {
                setFile(selectedFile);
                setResult(null);
            } else {
                toast({
                    title: 'Invalid file',
                    description: 'Please select an image file',
                    variant: 'destructive',
                });
            }
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;

        try {
            setAnalyzing(true);
            const analysis = await forensicsAPI.analyzeImage(file);
            setResult(analysis);
            toast({
                title: 'Analysis complete',
                description: `Authenticity: ${analysis.authenticity?.authentic ? 'Authentic' : 'Likely Manipulated'}`,
                variant: analysis.authenticity?.authentic ? 'success' : 'default',
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to analyze image',
                variant: 'destructive',
            });
        } finally {
            setAnalyzing(false);
        }
    };

    const getAuthenticityColor = (authentic: boolean) => {
        return authentic ? 'success' : 'error';
    };

    const getRiskColor = (riskScore: number) => {
        if (riskScore < 0.3) return 'success';
        if (riskScore < 0.6) return 'warning';
        return 'error';
    };

    return (
        <Container>
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl md:text-4xl font-bold text-black dark:text-white">Image Forensics</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        Analyze receipt authenticity and detect manipulation
                    </p>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle>Upload Image</CardTitle>
                        <CardDescription>Upload a receipt or invoice image to analyze its authenticity</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div
                                className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-12 text-center"
                            >
                                <input
                                    type="file"
                                    id="forensics-file-input"
                                    className="hidden"
                                    accept="image/*"
                                    onChange={handleFileSelect}
                                />
                                <label htmlFor="forensics-file-input" className="cursor-pointer">
                                    {file ? (
                                        <div className="space-y-4">
                                            <FileImage className="h-12 w-12 mx-auto text-black dark:text-white" />
                                            <div>
                                                <p className="font-semibold">{file.name}</p>
                                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                    {(file.size / 1024).toFixed(2)} KB
                                                </p>
                                            </div>
                                            <Button onClick={handleAnalyze} disabled={analyzing}>
                                                {analyzing ? 'Analyzing...' : 'Analyze Image'}
                                            </Button>
                                        </div>
                                    ) : (
                                        <div className="space-y-4">
                                            <Upload className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-600" />
                                            <div>
                                                <p className="font-semibold">Click to upload or drag and drop</p>
                                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                    JPEG, PNG (max 10MB)
                                                </p>
                                            </div>
                                        </div>
                                    )}
                                </label>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {result && (
                    <div className="space-y-4">
                        <Card>
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle>Analysis Results</CardTitle>
                                    <Badge variant={getAuthenticityColor(result.authenticity?.authentic) as any}>
                                        {result.authenticity?.authentic ? 'Authentic' : 'Likely Manipulated'}
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Authenticity</p>
                                            <p className="text-2xl font-bold">
                                                {result.authenticity?.authentic ? (
                                                    <span className="text-green-600 dark:text-green-400">Authentic</span>
                                                ) : (
                                                    <span className="text-red-600 dark:text-red-400">Manipulated</span>
                                                )}
                                            </p>
                                        </div>
                                        <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Confidence</p>
                                            <p className="text-2xl font-bold">
                                                {(result.authenticity?.confidence * 100).toFixed(0)}%
                                            </p>
                                        </div>
                                        <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Risk Score</p>
                                            <p className="text-2xl font-bold">
                                                {(result.authenticity?.risk_score * 100).toFixed(0)}%
                                            </p>
                                        </div>
                                    </div>

                                    {result.analysis && (
                                        <div className="space-y-3">
                                            <h3 className="font-semibold">Detailed Analysis</h3>
                                            {result.analysis.ela_analysis && (
                                                <div className="p-3 border border-gray-200 dark:border-gray-800 rounded-lg">
                                                    <p className="text-sm font-medium mb-1">ELA Analysis</p>
                                                    <p className="text-xs text-gray-600 dark:text-gray-400">
                                                        Score: {(result.analysis.ela_analysis.score * 100).toFixed(0)}%
                                                        {result.analysis.ela_analysis.anomalies_detected && ' • Anomalies detected'}
                                                    </p>
                                                </div>
                                            )}
                                            {result.analysis.exif_analysis && (
                                                <div className="p-3 border border-gray-200 dark:border-gray-800 rounded-lg">
                                                    <p className="text-sm font-medium mb-1">EXIF Analysis</p>
                                                    <p className="text-xs text-gray-600 dark:text-gray-400">
                                                        Score: {(result.analysis.exif_analysis.score * 100).toFixed(0)}%
                                                        {result.analysis.exif_analysis.camera_make && ` • ${result.analysis.exif_analysis.camera_make}`}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {result.manipulation_indicators && result.manipulation_indicators.length > 0 && (
                                        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                            <p className="text-sm font-medium mb-2">Manipulation Indicators</p>
                                            <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300 space-y-1">
                                                {result.manipulation_indicators.map((indicator: string, index: number) => (
                                                    <li key={index}>{indicator}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {result.recommendation && (
                                        <div className="p-4 border border-gray-200 dark:border-gray-800 rounded-lg">
                                            <p className="text-sm font-medium mb-2">Recommendation</p>
                                            <p className="text-sm text-gray-700 dark:text-gray-300">{result.recommendation}</p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                )}
            </div>
        </Container>
    );
}

