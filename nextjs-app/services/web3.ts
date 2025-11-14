import { ethers } from 'ethers';

// Contract ABI (minimal interface for the functions we need)
const AUDIT_STORAGE_ABI = [
    'function storeAudit(bytes32 _hash, string memory _pinataLink, string memory _auditId) public',
    'function getAudit(uint256 _index) public view returns (tuple(bytes32 hash, string pinataLink, string auditId, uint256 timestamp, address storedBy))',
    'function getAuditById(string memory _auditId) public view returns (tuple(bytes32 hash, string pinataLink, string auditId, uint256 timestamp, address storedBy))',
    'function getAuditCount() public view returns (uint256)',
    'function isHashStored(bytes32 _hash) public view returns (bool)',
    'event AuditStored(bytes32 indexed hash, string pinataLink, string auditId, uint256 timestamp, address indexed storedBy, uint256 index)',
];

export interface AuditRecord {
    hash: string;
    pinataLink: string;
    auditId: string;
    timestamp: bigint;
    storedBy: string;
}

class Web3Service {
    private provider: ethers.BrowserProvider | null = null;
    private signer: ethers.JsonRpcSigner | null = null;
    private contract: ethers.Contract | null = null;
    private contractAddress: string = '';

    // Sepolia testnet configuration
    private readonly SEPOLIA_CHAIN_ID = BigInt(11155111);
    private readonly SEPOLIA_NETWORK = {
        chainId: '0xaa36a7', // 11155111 in hex
        chainName: 'Sepolia',
        nativeCurrency: {
            name: 'Ether',
            symbol: 'ETH',
            decimals: 18,
        },
        rpcUrls: ['https://sepolia.infura.io/v3/'],
        blockExplorerUrls: ['https://sepolia.etherscan.io'],
    };

    /**
     * Switch to Sepolia network
     */
    async switchToSepolia(): Promise<void> {
        if (typeof window === 'undefined' || !window.ethereum) {
            throw new Error('MetaMask is not installed.');
        }

        try {
            // Try to switch to Sepolia
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: this.SEPOLIA_NETWORK.chainId }],
            });
        } catch (switchError: any) {
            // This error code indicates that the chain has not been added to MetaMask
            if (switchError.code === 4902) {
                try {
                    // Add Sepolia network to MetaMask
                    await window.ethereum.request({
                        method: 'wallet_addEthereumChain',
                        params: [this.SEPOLIA_NETWORK],
                    });
                } catch (addError) {
                    throw new Error('Failed to add Sepolia network to MetaMask');
                }
            } else {
                throw new Error('Failed to switch to Sepolia network');
            }
        }
    }

    /**
     * Check if connected to Sepolia
     */
    async isSepoliaNetwork(): Promise<boolean> {
        if (!this.provider) {
            return false;
        }
        try {
            const network = await this.provider.getNetwork();
            return network.chainId === this.SEPOLIA_CHAIN_ID;
        } catch {
            return false;
        }
    }

    /**
     * Connect to MetaMask wallet and ensure Sepolia network
     */
    async connectWallet(): Promise<string> {
        if (typeof window === 'undefined' || !window.ethereum) {
            throw new Error('MetaMask is not installed. Please install MetaMask to continue.');
        }

        try {
            // Request account access (this opens MetaMask)
            await window.ethereum.request({ method: 'eth_requestAccounts' });

            this.provider = new ethers.BrowserProvider(window.ethereum);
            this.signer = await this.provider.getSigner();
            const address = await this.signer.getAddress();

            // Check if on Sepolia, if not, switch
            const isSepolia = await this.isSepoliaNetwork();
            if (!isSepolia) {
                await this.switchToSepolia();
                // Reinitialize provider after network switch
                this.provider = new ethers.BrowserProvider(window.ethereum);
                this.signer = await this.provider.getSigner();
            }

            return address;
        } catch (error: any) {
            if (error.code === 4001) {
                throw new Error('Please connect to MetaMask');
            }
            throw new Error(error.message || 'Failed to connect wallet');
        }
    }

    /**
     * Get current connected address
     */
    async getAddress(): Promise<string | null> {
        if (!this.signer) {
            return null;
        }
        try {
            return await this.signer.getAddress();
        } catch {
            return null;
        }
    }

    /**
     * Initialize contract with address
     */
    initializeContract(contractAddress: string): void {
        if (!this.signer) {
            throw new Error('Wallet not connected. Please connect your wallet first.');
        }

        this.contractAddress = contractAddress;
        this.contract = new ethers.Contract(
            contractAddress,
            AUDIT_STORAGE_ABI,
            this.signer
        );
    }

    /**
     * Check if contract is initialized
     */
    isContractInitialized(): boolean {
        return this.contract !== null && this.contractAddress !== '';
    }

    /**
     * Store audit on-chain
     */
    async storeAudit(
        hash: string, // bytes32 hash (0x-prefixed)
        pinataLink: string,
        auditId: string
    ): Promise<ethers.ContractTransactionResponse> {
        if (!this.isContractInitialized()) {
            throw new Error('Contract not initialized. Please provide contract address.');
        }

        try {
            const tx = await this.contract!.storeAudit(hash, pinataLink, auditId);
            return tx;
        } catch (error: any) {
            throw new Error(
                error.reason || error.message || 'Failed to store audit on-chain'
            );
        }
    }

    /**
     * Wait for transaction confirmation
     */
    async waitForTransaction(
        tx: ethers.ContractTransactionResponse
    ): Promise<ethers.ContractTransactionReceipt> {
        if (!this.provider) {
            throw new Error('Provider not initialized');
        }
        // Use tx.wait() which returns ContractTransactionReceipt
        const receipt = await tx.wait();
        if (!receipt) {
            throw new Error('Transaction receipt not found');
        }
        return receipt;
    }

    /**
     * Get audit count
     */
    async getAuditCount(): Promise<bigint> {
        if (!this.isContractInitialized()) {
            throw new Error('Contract not initialized');
        }

        try {
            return await this.contract!.getAuditCount();
        } catch (error: any) {
            throw new Error('Failed to get audit count');
        }
    }

    /**
     * Get audit by index
     */
    async getAudit(index: number): Promise<AuditRecord> {
        if (!this.isContractInitialized()) {
            throw new Error('Contract not initialized');
        }

        try {
            const result = await this.contract!.getAudit(index);
            return {
                hash: result.hash,
                pinataLink: result.pinataLink,
                auditId: result.auditId,
                timestamp: result.timestamp,
                storedBy: result.storedBy,
            };
        } catch (error: any) {
            throw new Error('Failed to get audit');
        }
    }

    /**
     * Get all audits from the contract
     */
    async getAllAudits(): Promise<AuditRecord[]> {
        if (!this.isContractInitialized()) {
            throw new Error('Contract not initialized');
        }

        try {
            const count = await this.getAuditCount();
            const audits: AuditRecord[] = [];

            for (let i = 0; i < Number(count); i++) {
                const audit = await this.getAudit(i);
                audits.push(audit);
            }

            return audits;
        } catch (error: any) {
            throw new Error('Failed to get all audits');
        }
    }

    /**
     * Check if hash is already stored
     */
    async isHashStored(hash: string): Promise<boolean> {
        if (!this.isContractInitialized()) {
            throw new Error('Contract not initialized');
        }

        try {
            return await this.contract!.isHashStored(hash);
        } catch (error: any) {
            throw new Error('Failed to check hash');
        }
    }

    /**
     * Get network info
     */
    async getNetwork(): Promise<ethers.Network | null> {
        if (!this.provider) {
            return null;
        }
        try {
            return await this.provider.getNetwork();
        } catch {
            return null;
        }
    }

    /**
     * Ensure connected to Sepolia network
     */
    async ensureSepoliaNetwork(): Promise<void> {
        if (typeof window === 'undefined' || !window.ethereum) {
            throw new Error('MetaMask is not installed.');
        }

        const isSepolia = await this.isSepoliaNetwork();
        if (!isSepolia) {
            await this.switchToSepolia();
            // Reinitialize provider after network switch
            this.provider = new ethers.BrowserProvider(window.ethereum);
            this.signer = await this.provider.getSigner();
        }
    }
}

// Extend Window interface for TypeScript
declare global {
    interface Window {
        ethereum?: any;
    }
}

export const web3Service = new Web3Service();

