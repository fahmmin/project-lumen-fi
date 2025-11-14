'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { emailAPI } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';
import { useUser } from '@/contexts/UserContext';
import { Mail, Loader2, CheckCircle2, Copy, Wallet } from 'lucide-react';

export default function EmailPage() {
    const { userId, isConnected, connectWallet, isLoading: userLoading } = useUser();
    const [emailSubject, setEmailSubject] = useState<string>('');
    const [emailBody, setEmailBody] = useState<string>('');
    const [senderEmail, setSenderEmail] = useState<string>('');
    const [parsing, setParsing] = useState(false);
    const [testing, setTesting] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [exampleEmail, setExampleEmail] = useState<any>(null);
    const { toast } = useToast();

    useEffect(() => {
        loadExample();
    }, []);

    const loadExample = async () => {
        try {
            const data = await emailAPI.getExampleEmail();
            setExampleEmail(data.example);
        } catch (error) {
            console.error('Failed to load example:', error);
        }
    };

    const handleLoadExample = () => {
        if (exampleEmail) {
            setEmailSubject(exampleEmail.email_subject);
            setEmailBody(exampleEmail.email_body);
            setSenderEmail(exampleEmail.sender_email);
        }
    };

    const handleTestParser = async () => {
        if (!emailSubject || !emailBody) {
            toast({
                title: 'Error',
                description: 'Please enter email subject and body',
                variant: 'destructive',
            });
            return;
        }

        setTesting(true);
        try {
            const data = await emailAPI.testParser(emailSubject, emailBody);
            setResult(data);
            toast({
                title: 'Parser Test Complete',
                description: `Confidence: ${data.confidence_percentage}`,
                variant: 'success',
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to test parser',
                variant: 'destructive',
            });
        } finally {
            setTesting(false);
        }
    };

    const handleParseReceipt = async () => {
        if (!userId || !emailSubject || !emailBody) {
            toast({
                title: 'Error',
                description: 'Please enter user ID, email subject, and body',
                variant: 'destructive',
            });
            return;
        }

        setParsing(true);
        try {
            const data = await emailAPI.parseReceipt(userId, emailSubject, emailBody, senderEmail);
            toast({
                title: 'Receipt Parsed!',
                description: data.message || 'Email receipt processed successfully',
                variant: 'success',
            });
            setEmailSubject('');
            setEmailBody('');
            setSenderEmail('');
            setResult(null);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to parse email receipt',
                variant: 'destructive',
            });
        } finally {
            setParsing(false);
        }
    };

    return (
        <Container>
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold mb-2">Email Receipt Parser</h1>
                    <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                        Extract receipt information from email confirmations
                    </p>
                </div>

                {/* Wallet Connection */}
                {!isConnected && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Connect Wallet</CardTitle>
                            <CardDescription>Connect your wallet to parse email receipts</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button onClick={connectWallet} className="w-full sm:w-auto">
                                <Wallet className="h-4 w-4 mr-2" />
                                Connect Wallet
                            </Button>
                        </CardContent>
                    </Card>
                )}

                {/* Email Input */}
                <Card>
                    <CardHeader>
                        <CardTitle>Email Content</CardTitle>
                        <CardDescription>
                            Paste the email subject and body from a receipt confirmation
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {exampleEmail && (
                            <Button variant="outline" onClick={handleLoadExample} className="w-full sm:w-auto">
                                <Copy className="h-4 w-4 mr-2" />
                                Load Example Email
                            </Button>
                        )}
                        <Input
                            placeholder="Email Subject"
                            value={emailSubject}
                            onChange={(e) => setEmailSubject(e.target.value)}
                        />
                        <Input
                            placeholder="Sender Email (optional)"
                            value={senderEmail}
                            onChange={(e) => setSenderEmail(e.target.value)}
                        />
                        <Textarea
                            placeholder="Email Body"
                            value={emailBody}
                            onChange={(e) => setEmailBody(e.target.value)}
                            rows={10}
                            className="font-mono text-sm"
                        />
                        <div className="flex gap-2">
                            <Button
                                onClick={handleTestParser}
                                disabled={testing || !emailSubject || !emailBody}
                                variant="outline"
                                className="flex-1"
                            >
                                {testing ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        Testing...
                                    </>
                                ) : (
                                    <>
                                        <Mail className="h-4 w-4 mr-2" />
                                        Test Parser
                                    </>
                                )}
                            </Button>
                            <Button
                                onClick={handleParseReceipt}
                                disabled={parsing || !isConnected || !userId || !emailSubject || !emailBody}
                                className="flex-1"
                            >
                                {parsing ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        Parsing...
                                    </>
                                ) : (
                                    <>
                                        <CheckCircle2 className="h-4 w-4 mr-2" />
                                        Parse & Upload Receipt
                                    </>
                                )}
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Results */}
                {result && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Parser Results</CardTitle>
                            <CardDescription>
                                Confidence: <Badge>{result.confidence_percentage}</Badge>
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div>
                                    <h3 className="font-semibold mb-2">Extracted Fields</h3>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {result.extracted_fields?.vendor && (
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Vendor</p>
                                                <p className="font-semibold">{result.extracted_fields.vendor}</p>
                                            </div>
                                        )}
                                        {result.extracted_fields?.amount && (
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Amount</p>
                                                <p className="font-semibold">
                                                    ${result.extracted_fields.amount.toFixed(2)}
                                                </p>
                                            </div>
                                        )}
                                        {result.extracted_fields?.date && (
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Date</p>
                                                <p className="font-semibold">{result.extracted_fields.date}</p>
                                            </div>
                                        )}
                                        {result.extracted_fields?.category && (
                                            <div>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">Category</p>
                                                <p className="font-semibold">{result.extracted_fields.category}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div>
                                    <h3 className="font-semibold mb-2">Full Response</h3>
                                    <pre className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg text-xs overflow-auto">
                                        {JSON.stringify(result, null, 2)}
                                    </pre>
                                </div>
                            </div>
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
                            <p>1. Copy the subject and body from a receipt confirmation email</p>
                            <p>2. Paste them into the fields above</p>
                            <p>3. Click "Test Parser" to see what will be extracted (optional)</p>
                            <p>4. Click "Parse & Upload Receipt" to process and index it</p>
                            <p className="mt-4 font-semibold">Supported Email Types:</p>
                            <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-400">
                                <li>Order confirmations (Amazon, eBay, etc.)</li>
                                <li>Receipt emails from retailers</li>
                                <li>Transaction notifications</li>
                                <li>Invoice emails</li>
                            </ul>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </Container>
    );
}

