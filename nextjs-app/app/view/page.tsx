'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { web3Service, AuditRecord } from '@/services/web3';
import { pinataService } from '@/services/pinata';
import { decryptAuditReport, verifyHash } from '@/services/crypto';
import WalletConnect from '@/components/WalletConnect';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, Eye, Database, Wallet, ExternalLink, CheckCircle2 } from 'lucide-react';

export default function ViewPage() {
    const [walletAddress, setWalletAddress] = useState<string | null>(null);
    const [contractAddress, setContractAddress] = useState('');
    const [audits, setAudits] = useState<AuditRecord[]>([]);
    const [loading, setLoading] = useState(false);
    const [loadingAudits, setLoadingAudits] = useState(false);
    const [selectedAudit, setSelectedAudit] = useState<AuditRecord | null>(null);
    const [decryptedData, setDecryptedData] = useState<any>(null);
    const [decrypting, setDecrypting] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        const savedAddress = localStorage.getItem('contractAddress') ||
            (typeof window !== 'undefined' ? process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || '' : '');
        if (savedAddress) {
            setContractAddress(savedAddress);
        }
    }, []);

    const initializeContract = (address: string) => {
        try {
            web3Service.initializeContract(address);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to initialize contract',
                variant: 'destructive',
            });
        }
    };

    const handleWalletConnect = async (address: string) => {
        setWalletAddress(address);
        try {
            await web3Service.ensureSepoliaNetwork();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to switch to Sepolia network',
                variant: 'destructive',
            });
        }
        if (contractAddress) {
            initializeContract(contractAddress);
        }
    };

    const handleLoadAudits = async () => {
        if (!web3Service.isContractInitialized()) {
            toast({
                title: 'Error',
                description: 'Please provide contract address first',
                variant: 'destructive',
            });
            return;
        }

        setLoadingAudits(true);

        try {
            const allAudits = await web3Service.getAllAudits();
            setAudits(allAudits);
            toast({
                title: 'Success',
                description: `Loaded ${allAudits.length} audit(s)`,
                variant: 'success',
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to load audits',
                variant: 'destructive',
            });
        } finally {
            setLoadingAudits(false);
        }
    };

    const handleViewAudit = async (audit: AuditRecord) => {
        setSelectedAudit(audit);
        setDecryptedData(null);
        setDecrypting(true);

        try {
            const currentAddress = await web3Service.getAddress();
            const isCreator = currentAddress?.toLowerCase() === audit.storedBy.toLowerCase();

            if (!isCreator) {
                toast({
                    title: 'Error',
                    description: 'Only the audit creator can decrypt and view this report',
                    variant: 'destructive',
                });
                setDecrypting(false);
                return;
            }

            let encryptedData = await pinataService.fetchFromIPFS(audit.pinataLink);

            if (typeof encryptedData === 'string') {
                // Already a string
            } else if (encryptedData && typeof encryptedData === 'object') {
                if ('pinataContent' in encryptedData) {
                    const pinataContent = encryptedData.pinataContent;
                    if (pinataContent && typeof pinataContent === 'object' && 'encryptedData' in pinataContent) {
                        encryptedData = pinataContent.encryptedData;
                    } else if (typeof pinataContent === 'string') {
                        encryptedData = pinataContent;
                    } else {
                        encryptedData = JSON.stringify(pinataContent);
                    }
                } else if ('encryptedData' in encryptedData) {
                    encryptedData = encryptedData.encryptedData;
                } else {
                    const values = Object.values(encryptedData);
                    if (values.length === 1 && typeof values[0] === 'string') {
                        encryptedData = values[0] as string;
                    } else {
                        encryptedData = JSON.stringify(encryptedData);
                    }
                }
            } else {
                encryptedData = String(encryptedData);
            }

            if (typeof encryptedData !== 'string') {
                throw new Error('Failed to extract encrypted string from IPFS data');
            }

            const decrypted = decryptAuditReport(
                encryptedData,
                audit.storedBy.toLowerCase(),
                audit.auditId
            );

            const dataStructure = { encryptedData: encryptedData };
            const hashValid = verifyHash(dataStructure, audit.hash);
            if (!hashValid) {
                toast({
                    title: 'Warning',
                    description: 'Hash verification failed. Data may have been tampered with.',
                    variant: 'destructive',
                });
            }

            setDecryptedData(decrypted);
            toast({
                title: 'Success',
                description: 'Audit report decrypted successfully!',
                variant: 'success',
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to decrypt audit report',
                variant: 'destructive',
            });
        } finally {
            setDecrypting(false);
        }
    };

    const formatDate = (timestamp: bigint) => {
        return new Date(Number(timestamp) * 1000).toLocaleString();
    };

    const formatAddress = (addr: string) => {
        return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
    };

    return (
        <Container>
            <div className="max-w-6xl mx-auto space-y-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">View Audit Reports</h1>
                    <p className="text-gray-600">
                        View and decrypt your stored audit reports from the blockchain
                    </p>
                </div>

                <div className="space-y-6">
                    {/* Wallet Connection */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Wallet className="h-5 w-5" />
                                1. Connect Wallet
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <WalletConnect onConnect={handleWalletConnect} />
                            {walletAddress && (
                                <p className="mt-4 text-sm text-gray-600">
                                    Connected: <span className="font-mono">{walletAddress}</span>
                                </p>
                            )}
                        </CardContent>
                    </Card>

                    {/* Contract Address */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Database className="h-5 w-5" />
                                2. Contract Address
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex gap-4">
                                <Input
                                    type="text"
                                    value={contractAddress}
                                    onChange={(e) => {
                                        const addr = e.target.value;
                                        setContractAddress(addr);
                                        localStorage.setItem('contractAddress', addr);
                                        if (walletAddress && addr) {
                                            initializeContract(addr);
                                        }
                                    }}
                                    placeholder="0x..."
                                    className="flex-1 font-mono"
                                />
                                <Button
                                    onClick={handleLoadAudits}
                                    disabled={loadingAudits || !contractAddress || !web3Service.isContractInitialized()}
                                >
                                    {loadingAudits ? (
                                        <>
                                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                            Loading...
                                        </>
                                    ) : (
                                        'Load Audits'
                                    )}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Audits List */}
                    {audits.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>3. Audit Reports ({audits.length})</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {audits.map((audit, index) => {
                                        const isCreator = walletAddress?.toLowerCase() === audit.storedBy.toLowerCase();
                                        return (
                                            <div
                                                key={index}
                                                className="p-4 border border-gray-200 rounded-lg hover:border-black transition-colors"
                                            >
                                                <div className="flex items-start justify-between">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <h3 className="font-semibold text-lg">
                                                                {audit.auditId}
                                                            </h3>
                                                            {isCreator && (
                                                                <Badge variant="success">Your Audit</Badge>
                                                            )}
                                                        </div>
                                                        <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-400 mb-2">
                                                            <div>
                                                                <span className="font-medium">Stored By:</span>{' '}
                                                                <span className="font-mono">{formatAddress(audit.storedBy)}</span>
                                                            </div>
                                                            <div>
                                                                <span className="font-medium">Date:</span>{' '}
                                                                {formatDate(audit.timestamp)}
                                                            </div>
                                                            <div>
                                                                <span className="font-medium">Hash:</span>{' '}
                                                                <span className="font-mono text-xs">{formatAddress(audit.hash)}</span>
                                                            </div>
                                                            <div>
                                                                <a
                                                                    href={audit.pinataLink}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-black hover:underline text-xs flex items-center gap-1"
                                                                >
                                                                    <ExternalLink className="h-3 w-3" />
                                                                    View on IPFS
                                                                </a>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <Button
                                                        onClick={() => handleViewAudit(audit)}
                                                        disabled={!isCreator || decrypting}
                                                        variant="outline"
                                                    >
                                                        {decrypting && selectedAudit?.auditId === audit.auditId ? (
                                                            <>
                                                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                                Decrypting...
                                                            </>
                                                        ) : isCreator ? (
                                                            <>
                                                                <Eye className="h-4 w-4 mr-2" />
                                                                View & Decrypt
                                                            </>
                                                        ) : (
                                                            'View Only'
                                                        )}
                                                    </Button>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Decrypted Data Display */}
                    {selectedAudit && decryptedData && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <CheckCircle2 className="h-5 w-5" />
                                    Decrypted Audit Report
                                </CardTitle>
                                <CardDescription>
                                    Audit ID: {selectedAudit.auditId}
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                        <span className="font-medium">Stored By:</span>{' '}
                                        <span className="font-mono">{formatAddress(selectedAudit.storedBy)}</span>
                                    </p>
                                </div>
                                <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
                                    <pre className="text-sm bg-gray-50 dark:bg-gray-900 p-4 rounded overflow-auto max-h-96 text-gray-900 dark:text-gray-100">
                                        {JSON.stringify(decryptedData, null, 2)}
                                    </pre>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {loadingAudits && (
                        <Card>
                            <CardContent className="py-12">
                                <div className="flex justify-center">
                                    <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {!loadingAudits && audits.length === 0 && contractAddress && (
                        <EmptyState
                            title="No audits found"
                            description="Click 'Load Audits' to fetch from blockchain"
                            icon={<Database className="h-12 w-12" />}
                        />
                    )}
                </div>
            </div>
        </Container>
    );
}
