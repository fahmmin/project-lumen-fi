export interface PinataUploadResult {
    IpfsHash: string;
    PinSize: number;
    Timestamp: string;
    isDuplicate?: boolean;
}

class PinataService {
    private apiKey: string = '';

    /**
     * Initialize Pinata with JWT API key from environment or parameter
     */
    initialize(apiKey?: string): void {
        // Use provided key or get from environment (client-side)
        if (apiKey) {
            this.apiKey = apiKey;
        } else if (typeof window !== 'undefined') {
            // Client-side: get from NEXT_PUBLIC_ env var
            this.apiKey = process.env.NEXT_PUBLIC_PINATA_API_KEY || '';
        } else {
            // Server-side fallback
            this.apiKey = process.env.NEXT_PUBLIC_PINATA_API_KEY || '';
        }

        if (!this.apiKey) {
            throw new Error('Pinata API key not found. Please set NEXT_PUBLIC_PINATA_API_KEY in .env.local');
        }
    }

    /**
     * Check if Pinata is initialized
     */
    isInitialized(): boolean {
        // Auto-initialize from env if not already initialized
        if (!this.apiKey && typeof window !== 'undefined') {
            this.apiKey = process.env.NEXT_PUBLIC_PINATA_API_KEY || '';
        }
        return this.apiKey !== '';
    }

    /**
     * Upload a file to Pinata IPFS using REST API
     */
    async uploadFile(file: File): Promise<PinataUploadResult> {
        if (!this.isInitialized()) {
            throw new Error('Pinata not initialized. Please provide API key.');
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            const metadata = JSON.stringify({
                name: file.name,
                keyvalues: {
                    uploadedAt: new Date().toISOString(),
                },
            });
            formData.append('pinataMetadata', metadata);

            const options = JSON.stringify({
                cidVersion: 0,
            });
            formData.append('pinataOptions', options);

            const response = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${this.apiKey}`,
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.error?.details || `Upload failed: ${response.statusText}`
                );
            }

            const data = await response.json();
            return data;
        } catch (error: any) {
            throw new Error(
                error.message || 'Failed to upload file to Pinata'
            );
        }
    }

    /**
     * Upload JSON data to Pinata IPFS using REST API
     */
    async uploadJSON(data: any, name: string = 'data.json'): Promise<PinataUploadResult> {
        if (!this.isInitialized()) {
            throw new Error('Pinata not initialized. Please provide API key.');
        }

        try {
            const body = {
                pinataContent: data,
                pinataMetadata: {
                    name: name,
                    keyvalues: {
                        uploadedAt: new Date().toISOString(),
                    },
                },
                pinataOptions: {
                    cidVersion: 0,
                },
            };

            const response = await fetch('https://api.pinata.cloud/pinning/pinJSONToIPFS', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${this.apiKey}`,
                },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.error?.details || `Upload failed: ${response.statusText}`
                );
            }

            const result = await response.json();
            return result;
        } catch (error: any) {
            throw new Error(
                error.message || 'Failed to upload JSON to Pinata'
            );
        }
    }

    /**
     * Get IPFS gateway URL from hash
     */
    getGatewayURL(hash: string): string {
        return `https://gateway.pinata.cloud/ipfs/${hash}`;
    }

    /**
     * Fetch data from IPFS using Pinata gateway
     */
    async fetchFromIPFS(ipfsHash: string): Promise<any> {
        try {
            // Extract hash from full URL if provided
            const hash = ipfsHash.includes('/ipfs/')
                ? ipfsHash.split('/ipfs/')[1].split('?')[0] // Remove query params if any
                : ipfsHash.split('?')[0];

            const url = this.getGatewayURL(hash);

            // Try multiple gateways for better reliability
            const gateways = [
                url, // Pinata gateway
                `https://ipfs.io/ipfs/${hash}`, // Public IPFS gateway
                `https://gateway.ipfs.io/ipfs/${hash}`, // Alternative gateway
            ];

            let lastError: Error | null = null;

            for (const gatewayUrl of gateways) {
                try {
                    const response = await fetch(gatewayUrl, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json, text/plain, */*',
                        },
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    // Try to parse as JSON first
                    const contentType = response.headers.get('content-type') || '';
                    if (contentType.includes('application/json')) {
                        const jsonData = await response.json();
                        // If it's wrapped in pinataContent, extract it
                        if (jsonData && typeof jsonData === 'object' && 'pinataContent' in jsonData) {
                            return jsonData.pinataContent;
                        }
                        return jsonData;
                    } else {
                        // Return as text
                        const textData = await response.text();
                        // Try to parse as JSON if it looks like JSON
                        try {
                            const parsed = JSON.parse(textData);
                            if (parsed && typeof parsed === 'object' && 'pinataContent' in parsed) {
                                return parsed.pinataContent;
                            }
                            return parsed;
                        } catch {
                            return textData;
                        }
                    }
                } catch (error: any) {
                    lastError = error;
                    // Try next gateway
                    continue;
                }
            }

            // If all gateways failed
            throw lastError || new Error('All IPFS gateways failed');
        } catch (error: any) {
            throw new Error(`Failed to fetch from IPFS: ${error.message}`);
        }
    }
}

export const pinataService = new PinataService();

