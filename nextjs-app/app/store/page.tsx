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
import { auditAPI } from '@/services/api';
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
    const [autoMode, setAutoMode] = useState(false);
    const { toast } = useToast();

    const fetchAuditData = async (id: string) => {
        try {
            setLoading(true);
            const auditData = await auditAPI.getAuditById(id);

            // Parse the audit data - it might be in different formats
            let auditJson: any;
            if (typeof auditData === 'string') {
                // Try to extract JSON from string
                try {
                    auditJson = JSON.parse(auditData);
                } catch {
                    // If it's not JSON, try to find JSON in the content
                    const jsonMatch = auditData.match(/\{[\s\S]*\}/);
                    if (jsonMatch) {
                        auditJson = JSON.parse(jsonMatch[0]);
                    } else {
                        throw new Error('Could not parse audit data');
                    }
                }
            } else if (auditData.content) {
                // If it's an object with content field
                if (typeof auditData.content === 'string') {
                    const jsonMatch = auditData.content.match(/\{[\s\S]*\}/);
                    if (jsonMatch) {
                        auditJson = JSON.parse(jsonMatch[0]);
                    } else {
                        auditJson = auditData;
                    }
                } else {
                    auditJson = auditData.content;
                }
            } else {
                auditJson = auditData;
            }

            // Set the audit report JSON
            setAuditReportJSON(JSON.stringify(auditJson, null, 2));

            toast({
                title: 'Success',
                description: 'Audit data loaded successfully',
                variant: 'success',
            });
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.message || 'Failed to fetch audit data',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

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

        // Check if audit ID is provided in URL params
        if (typeof window !== 'undefined') {
            const urlParams = new URLSearchParams(window.location.search);
            const auditIdParam = urlParams.get('auditId');
            if (auditIdParam) {
                setAuditId(auditIdParam);
                setAutoMode(true);
                // Auto-fetch audit data
                fetchAuditData(auditIdParam);
            }
        }
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
        // If in auto mode, do the full automatic flow
        if (autoMode && auditId) {
            // If we don't have audit data yet, fetch it first
            if (!auditReportJSON) {
                toast({
                    title: 'Loading audit data...',
                    description: 'Please wait while we fetch the audit data',
                    variant: 'default',
                });
                await fetchAuditData(auditId);
                // Wait a bit for state to update
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            // Now proceed with the full flow
            if (auditReportJSON) {
                await handleAutoStoreFlow();
                return;
            } else {
                toast({
                    title: 'Error',
                    description: 'Failed to load audit data. Please try again.',
                    variant: 'destructive',
                });
                return;
            }
        }

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
            setAutoMode(false);
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

    const handleAutoStoreFlow = async () => {
        setStoring(true);

        try {
            // Step 1: Connect wallet if not connected
            let currentAddress = walletAddress;
            if (!currentAddress) {
                toast({
                    title: 'Connecting wallet...',
                    description: 'Please approve the connection in MetaMask',
                    variant: 'default',
                });
                currentAddress = await web3Service.connectWallet();
                setWalletAddress(currentAddress);

                // Ensure we're on the right network
                await web3Service.ensureSepoliaNetwork();
                await loadNetworkInfo();
            }

            // Step 2: Initialize contract if not initialized
            if (!web3Service.isContractInitialized()) {
                if (!contractAddress) {
                    const savedAddress = localStorage.getItem('contractAddress') ||
                        (typeof window !== 'undefined' ? process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || '' : '');
                    if (savedAddress) {
                        setContractAddress(savedAddress);
                        web3Service.initializeContract(savedAddress);
                    } else {
                        throw new Error('Contract address not found. Please set it first.');
                    }
                } else {
                    web3Service.initializeContract(contractAddress);
                }
            }

            // Step 3: Encrypt and upload to IPFS
            if (!hash || !pinataLink) {
                toast({
                    title: 'Processing audit...',
                    description: 'Encrypting and uploading to IPFS...',
                    variant: 'default',
                });

                const jsonData = JSON.parse(auditReportJSON);
                const encryptedData = encryptAuditReport(jsonData, currentAddress!, auditId);
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
                    description: 'Audit report encrypted and uploaded to IPFS!',
                    variant: 'success',
                });
            }

            // Step 4: Check if hash already exists
            const exists = await web3Service.isHashStored(hash!);
            if (exists) {
                toast({
                    title: 'Error',
                    description: 'This audit hash is already stored on-chain',
                    variant: 'destructive',
                });
                setStoring(false);
                return;
            }

            // Step 5: Store on blockchain (this will open MetaMask in the same window)
            toast({
                title: 'Ready to store',
                description: 'Please confirm the transaction in MetaMask',
                variant: 'default',
            });

            const tx = await web3Service.storeAudit(hash!, pinataLink, auditId);
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
            setAutoMode(false);
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
                            {autoMode && (
                                <CardDescription>
                                    Auto mode: Will automatically fetch audit data, encrypt, upload, and store on blockchain
                                </CardDescription>
                            )}
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Button
                                onClick={handleStoreOnChain}
                                disabled={storing || (!autoMode && (!walletAddress || !hash || !pinataLink || !auditId)) || (autoMode && !auditId)}
                                className="w-full"
                            >
                                {storing ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        {autoMode ? 'Processing & Storing...' : 'Storing...'}
                                    </>
                                ) : (
                                    autoMode ? 'Store on Blockchain (Auto)' : 'Store Audit on Blockchain'
                                )}
                            </Button>
                            <p className="text-sm text-gray-600">
                                {autoMode
                                    ? 'This will automatically fetch the audit data, encrypt it, upload to IPFS, and store on the blockchain. MetaMask will open in this window for transaction confirmation.'
                                    : 'This will store the hash of your audit report and Pinata link on the blockchain. Make sure you have enough ETH for gas fees.'}
                            </p>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </Container>
    );
}
