'use client';

import { useState, useEffect } from 'react';
import { Container } from '@/components/layout/Container';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { web3Service } from '@/services/web3';
import { pinataService } from '@/services/pinata';
import { hashJSONToBytes32, encryptAuditReport } from '@/services/crypto';
import WalletConnect from '@/components/WalletConnect';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, CheckCircle2, Link as LinkIcon, Database, Wallet } from 'lucide-react';

export default function StorePage() {
    const [walletAddress, setWalletAddress] = useState<string | null>(null);
    const [contractAddress, setContractAddress] = useState('');
    const [auditReportJSON, setAuditReportJSON] = useState('');
    const [pinataLink, setPinataLink] = useState('');
    const [auditId, setAuditId] = useState('');
    const [loading, setLoading] = useState(false);
    const [storing, setStoring] = useState(false);
    const [hash, setHash] = useState<string | null>(null);
    const [auditCount, setAuditCount] = useState<number | null>(null);
    const [networkInfo, setNetworkInfo] = useState<string>('');
    const { toast } = useToast();

    useEffect(() => {
        const savedAddress = localStorage.getItem('contractAddress') ||
            (typeof window !== 'undefined' ? process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || '' : '');
        if (savedAddress) {
            setContractAddress(savedAddress);
            if (walletAddress) {
                initializeContract(savedAddress);
            }
        }
        loadNetworkInfo();
    }, [walletAddress]);

    const loadNetworkInfo = async () => {
        try {
            const network = await web3Service.getNetwork();
            if (network) {
                if (network.chainId === BigInt(11155111)) {
                    setNetworkInfo('Sepolia Testnet');
                } else if (network.chainId === BigInt(31337)) {
                    setNetworkInfo('Local Hardhat');
                } else {
                    setNetworkInfo(`Chain ID: ${network.chainId}`);
                }
            }
        } catch (error) {
            // Ignore
        }
    };

    const initializeContract = (address: string) => {
        try {
            web3Service.initializeContract(address);
            loadAuditCount();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to initialize contract',
                variant: 'destructive',
            });
        }
    };

    const loadAuditCount = async () => {
        if (!web3Service.isContractInitialized()) return;
        try {
            const count = await web3Service.getAuditCount();
            setAuditCount(Number(count));
        } catch (error) {
            // Ignore errors
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
        await loadNetworkInfo();
        if (contractAddress) {
            initializeContract(contractAddress);
        }
    };

    const handleContractAddressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const address = e.target.value;
        setContractAddress(address);
        localStorage.setItem('contractAddress', address);
        if (walletAddress && address) {
            initializeContract(address);
        }
    };

    const handleHashAudit = async () => {
        if (!auditReportJSON.trim()) {
            toast({
                title: 'Error',
                description: 'Please enter audit report JSON',
                variant: 'destructive',
            });
            return;
        }

        if (!walletAddress) {
            toast({
                title: 'Error',
                description: 'Please connect your wallet first',
                variant: 'destructive',
            });
            return;
        }

        if (!auditId.trim()) {
            toast({
                title: 'Error',
                description: 'Please enter audit ID first',
                variant: 'destructive',
            });
            return;
        }

        setLoading(true);

        try {
            const jsonData = JSON.parse(auditReportJSON);
            const encryptedData = encryptAuditReport(jsonData, walletAddress, auditId);
            pinataService.initialize();
            const dataToUpload = { encryptedData: encryptedData };
            const uploadResult = await pinataService.uploadJSON(
                dataToUpload,
                `audit_${auditId}_encrypted.json`
            );

            const pinataURL = pinataService.getGatewayURL(uploadResult.IpfsHash);
            setPinataLink(pinataURL);
            const hashValue = hashJSONToBytes32(dataToUpload);
            setHash(hashValue);

            toast({
                title: 'Success',
                description: 'Audit report encrypted, uploaded to IPFS, and hashed successfully!',
                variant: 'success',
            });
        } catch (error: any) {
            if (error instanceof SyntaxError) {
                toast({
                    title: 'Error',
                    description: 'Invalid JSON format. Please check your input.',
                    variant: 'destructive',
                });
            } else {
                toast({
                    title: 'Error',
                    description: error.message || 'Failed to process audit report',
                    variant: 'destructive',
                });
            }
        } finally {
            setLoading(false);
        }
    };

    const handleStoreOnChain = async () => {
        if (!walletAddress) {
            toast({
                title: 'Error',
                description: 'Please connect your wallet first',
                variant: 'destructive',
            });
            return;
        }

        if (!web3Service.isContractInitialized()) {
            toast({
                title: 'Error',
                description: 'Please provide contract address',
                variant: 'destructive',
            });
            return;
        }

        if (!hash) {
            toast({
                title: 'Error',
                description: 'Please hash the audit report first',
                variant: 'destructive',
            });
            return;
        }

        if (!pinataLink.trim()) {
            toast({
                title: 'Error',
                description: 'Please enter Pinata link',
                variant: 'destructive',
            });
            return;
        }

        if (!auditId.trim()) {
            toast({
                title: 'Error',
                description: 'Please enter audit ID',
                variant: 'destructive',
            });
            return;
        }

        setStoring(true);

        try {
            const exists = await web3Service.isHashStored(hash);
            if (exists) {
                toast({
                    title: 'Error',
                    description: 'This audit hash is already stored on-chain',
                    variant: 'destructive',
                });
                setStoring(false);
                return;
            }

            const tx = await web3Service.storeAudit(hash, pinataLink, auditId);
            toast({
                title: 'Transaction sent',
                description: 'Waiting for confirmation...',
                variant: 'default',
            });

            const receipt = await web3Service.waitForTransaction(tx);

            toast({
                title: 'Success',
                description: `Audit stored successfully! Transaction: ${receipt.hash}`,
                variant: 'success',
            });

            await loadAuditCount();
            setHash(null);
            setAuditReportJSON('');
            setPinataLink('');
            setAuditId('');
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to store audit on-chain',
                variant: 'destructive',
            });
        } finally {
            setStoring(false);
        }
    };

    return (
        <Container>
            <div className="max-w-4xl mx-auto space-y-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Store Audit on Blockchain</h1>
                    <p className="text-gray-600">
                        Encrypt, upload to IPFS, and store audit reports on the blockchain
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
                                <div className="mt-4 space-y-2">
                                    <p className="text-sm text-gray-600">
                                        Connected: <span className="font-mono">{walletAddress}</span>
                                    </p>
                                    {networkInfo && (
                                        <div>
                                            <p className="text-sm text-gray-600">
                                                Network: <Badge variant="outline">{networkInfo}</Badge>
                                            </p>
                                        </div>
                                    )}
                                </div>
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
                        <CardContent className="space-y-4">
                            <Input
                                type="text"
                                value={contractAddress}
                                onChange={handleContractAddressChange}
                                placeholder="0x..."
                                className="font-mono"
                            />
                            {auditCount !== null && (
                                <p className="text-sm text-green-600">
                                    Contract initialized. Total audits stored: <strong>{auditCount}</strong>
                                </p>
                            )}
                        </CardContent>
                    </Card>

                    {/* Audit ID */}
                    <Card>
                        <CardHeader>
                            <CardTitle>3. Audit ID</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <Input
                                type="text"
                                value={auditId}
                                onChange={(e) => setAuditId(e.target.value)}
                                placeholder="audit_123"
                            />
                        </CardContent>
                    </Card>

                    {/* Audit Report JSON */}
                    <Card>
                        <CardHeader>
                            <CardTitle>4. Audit Report JSON</CardTitle>
                            <CardDescription>
                                Paste your audit report JSON here. It will be encrypted using your wallet address.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Textarea
                                value={auditReportJSON}
                                onChange={(e) => setAuditReportJSON(e.target.value)}
                                placeholder='{"audit_id": "audit_123", "findings": {...}}'
                                rows={10}
                                className="font-mono text-sm"
                            />
                            <Button
                                onClick={handleHashAudit}
                                disabled={loading || !auditReportJSON.trim() || !auditId.trim() || !walletAddress}
                                className="w-full"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        Encrypting & Uploading...
                                    </>
                                ) : (
                                    'Encrypt, Upload to IPFS & Hash'
                                )}
                            </Button>
                            {hash && (
                                <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
                                    <div className="flex items-center gap-2">
                                        <CheckCircle2 className="h-4 w-4 text-black" />
                                        <span className="text-sm font-medium">Encrypted & Uploaded!</span>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-600 mb-1">Hash (bytes32):</p>
                                        <code className="text-xs bg-white px-2 py-1 rounded break-all block">
                                            {hash}
                                        </code>
                                    </div>
                                    {pinataLink && (
                                        <div>
                                            <p className="text-xs text-gray-600 mb-1">IPFS Link:</p>
                                            <a
                                                href={pinataLink}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs text-black hover:underline break-all flex items-center gap-1"
                                            >
                                                <LinkIcon className="h-3 w-3" />
                                                {pinataLink}
                                            </a>
                                        </div>
                                    )}
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Store Button */}
                    <Card>
                        <CardHeader>
                            <CardTitle>5. Store on Blockchain</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Button
                                onClick={handleStoreOnChain}
                                disabled={storing || !walletAddress || !hash || !pinataLink || !auditId}
                                className="w-full"
                            >
                                {storing ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        Storing...
                                    </>
                                ) : (
                                    'Store Audit on Blockchain'
                                )}
                            </Button>
                            <p className="text-sm text-gray-600">
                                This will store the hash of your audit report and Pinata link on the blockchain.
                                Make sure you have enough ETH for gas fees.
                            </p>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </Container>
    );
}
