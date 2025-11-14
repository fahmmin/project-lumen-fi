'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { voiceAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { Mic, Upload, Loader2, CheckCircle2, FileAudio, Wallet } from 'lucide-react';

export default function VoicePage() {
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [audioFile, setAudioFile] = useState<File | null>(null);
    const [transcribing, setTranscribing] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [transcription, setTranscription] = useState<any>(null);
    const [supportedFormats, setSupportedFormats] = useState<string[]>([]);
    const { toast } = useToast();

    useEffect(() => {
        loadSupportedFormats();
    }, []);

    const loadSupportedFormats = async () => {
        try {
            const data = await voiceAPI.getSupportedFormats();
            setSupportedFormats(data.supported_formats || []);
        } catch (error) {
            console.error('Failed to load supported formats:', error);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setAudioFile(e.target.files[0]);
            setTranscription(null);
        }
    };

    const handleTranscribe = async () => {
        if (!audioFile) {
            toast({
                title: 'Error',
                description: 'Please select an audio file',
                variant: 'destructive',
            });
            return;
        }

        setTranscribing(true);
        try {
            const result = await voiceAPI.transcribeAudio(audioFile);
            setTranscription(result);
            toast({
                title: 'Transcription Complete',
                description: 'Audio transcribed successfully',
                variant: 'success',
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to transcribe audio',
                variant: 'destructive',
            });
        } finally {
            setTranscribing(false);
        }
    };

    const handleUploadReceipt = async () => {
        if (!audioFile || !userId) {
            toast({
                title: 'Error',
                description: 'Please select an audio file and enter user ID',
                variant: 'destructive',
            });
            return;
        }

        setUploading(true);
        try {
            const result = await voiceAPI.uploadReceiptByVoice(audioFile, userId);
            toast({
                title: 'Receipt Uploaded!',
                description: result.message || 'Voice receipt processed and indexed successfully',
                variant: 'success',
            });
            setAudioFile(null);
            setTranscription(null);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to upload receipt',
                variant: 'destructive',
            });
        } finally {
            setUploading(false);
        }
    };

    return (
        <Container>
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold mb-2">Voice Receipt Upload</h1>
                    <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                        Upload receipts by speaking them aloud
                    </p>
                </div>

                {/* Wallet Connection */}
                {!isConnected && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Connect Wallet</CardTitle>
                            <CardDescription>Connect your wallet to upload voice receipts</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button onClick={connectWallet} className="w-full sm:w-auto">
                                <Wallet className="h-4 w-4 mr-2" />
                                Connect Wallet
                            </Button>
                        </CardContent>
                    </Card>
                )}

                {/* File Upload */}
                <Card>
                    <CardHeader>
                        <CardTitle>Upload Audio File</CardTitle>
                        <CardDescription>
                            Supported formats: {supportedFormats.join(', ')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center">
                            <input
                                type="file"
                                id="audio-upload"
                                accept={supportedFormats.join(',')}
                                onChange={handleFileSelect}
                                className="hidden"
                            />
                            <label htmlFor="audio-upload" className="cursor-pointer">
                                {audioFile ? (
                                    <div className="space-y-2">
                                        <FileAudio className="h-12 w-12 mx-auto text-black dark:text-white" />
                                        <p className="font-semibold">{audioFile.name}</p>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">
                                            {(audioFile.size / 1024).toFixed(2)} KB
                                        </p>
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        <Upload className="h-12 w-12 mx-auto text-gray-400" />
                                        <p className="font-semibold">Click to upload audio file</p>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">
                                            MP3, WAV, M4A, OGG, WebM
                                        </p>
                                    </div>
                                )}
                            </label>
                        </div>

                        {audioFile && (
                            <div className="flex gap-2">
                                <Button
                                    onClick={handleTranscribe}
                                    disabled={transcribing}
                                    variant="outline"
                                    className="flex-1"
                                >
                                    {transcribing ? (
                                        <>
                                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                            Transcribing...
                                        </>
                                    ) : (
                                        <>
                                            <Mic className="h-4 w-4 mr-2" />
                                            Transcribe Only
                                        </>
                                    )}
                                </Button>
                                <Button
                                    onClick={handleUploadReceipt}
                                    disabled={uploading || !isConnected || !userId}
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
                                            Upload Receipt
                                        </>
                                    )}
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Transcription Results */}
                {transcription && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Transcription Results</CardTitle>
                            <CardDescription>
                                Method: {transcription.method}
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <h3 className="font-semibold mb-2">Transcribed Text</h3>
                                <p className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                    {transcription.transcribed_text}
                                </p>
                            </div>

                            {transcription.extracted_fields && (
                                <div>
                                    <h3 className="font-semibold mb-2">Extracted Fields</h3>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {transcription.extracted_fields.vendor && (
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Vendor</p>
                                                <p className="font-semibold">{transcription.extracted_fields.vendor}</p>
                                            </div>
                                        )}
                                        {transcription.extracted_fields.amount && (
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Amount</p>
                                                <p className="font-semibold">
                                                    ${transcription.extracted_fields.amount.toFixed(2)}
                                                </p>
                                            </div>
                                        )}
                                        {transcription.extracted_fields.date && (
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Date</p>
                                                <p className="font-semibold">{transcription.extracted_fields.date}</p>
                                            </div>
                                        )}
                                        {transcription.extracted_fields.category && (
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Category</p>
                                                <p className="font-semibold">{transcription.extracted_fields.category}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                )}

                {/* Instructions */}
                <Card>
                    <CardHeader>
                        <CardTitle>How to Use</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2 text-sm">
                            <p>1. Record yourself describing a receipt, for example:</p>
                            <p className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg italic">
                                "I spent 59 dollars and 99 cents at Whole Foods on groceries including milk, bread, and vegetables on December 10th"
                            </p>
                            <p>2. Save the recording as an audio file (MP3, WAV, etc.)</p>
                            <p>3. Upload the file above</p>
                            <p>4. Click "Upload Receipt" to process and index it</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </Container>
    );
}

