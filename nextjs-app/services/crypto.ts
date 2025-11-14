import CryptoJS from 'crypto-js';

/**
 * Hash a JSON object using SHA-256
 * @param data The data to hash (object, string, or any JSON-serializable value)
 * @returns The SHA-256 hash as a hex string
 */
export function hashJSON(data: any): string {
    const jsonString = typeof data === 'string' ? data : JSON.stringify(data);
    return CryptoJS.SHA256(jsonString).toString(CryptoJS.enc.Hex);
}

/**
 * Convert a hex string to bytes32 format (for Solidity)
 * @param hexString The hex string (64 characters)
 * @returns The bytes32 value (0x-prefixed hex string)
 */
export function hexToBytes32(hexString: string): string {
    // Remove 0x prefix if present
    const cleanHex = hexString.startsWith('0x') ? hexString.slice(2) : hexString;

    // Ensure it's 64 characters (32 bytes)
    if (cleanHex.length !== 64) {
        throw new Error(`Hex string must be 64 characters, got ${cleanHex.length}`);
    }

    return '0x' + cleanHex;
}

/**
 * Hash JSON and convert to bytes32 format for Solidity
 * @param data The data to hash
 * @returns The bytes32 hash (0x-prefixed)
 */
export function hashJSONToBytes32(data: any): string {
    const hash = hashJSON(data);
    return hexToBytes32(hash);
}

/**
 * Generate encryption key from wallet address
 * This ensures only the wallet owner can decrypt
 * @param walletAddress The wallet address (will be normalized to lowercase)
 * @param auditId The audit ID for additional uniqueness
 * @returns Encryption key
 */
export function generateEncryptionKey(walletAddress: string, auditId: string): string {
    // Normalize address to lowercase for consistency
    const normalizedAddress = walletAddress.toLowerCase();
    // Combine wallet address and audit ID, then hash to create a key
    const combined = `${normalizedAddress}-${auditId}`;
    return CryptoJS.SHA256(combined).toString();
}

/**
 * Encrypt audit report data
 * @param data The audit report data (object or string)
 * @param walletAddress The wallet address of the creator (will be normalized to lowercase)
 * @param auditId The audit ID
 * @returns Encrypted data as a string
 */
export function encryptAuditReport(
    data: any,
    walletAddress: string,
    auditId: string
): string {
    // Normalize address to lowercase for consistency
    const normalizedAddress = walletAddress.toLowerCase();
    const jsonString = typeof data === 'string' ? data : JSON.stringify(data);
    const key = generateEncryptionKey(normalizedAddress, auditId);

    // Encrypt using AES
    const encrypted = CryptoJS.AES.encrypt(jsonString, key).toString();
    return encrypted;
}

/**
 * Decrypt audit report data
 * @param encryptedData The encrypted data (string or object that might contain the encrypted string)
 * @param walletAddress The wallet address of the creator
 * @param auditId The audit ID
 * @returns Decrypted data as JSON object
 */
export function decryptAuditReport(
    encryptedData: any,
    walletAddress: string,
    auditId: string
): any {
    try {
        // Normalize wallet address to lowercase for consistent key generation
        const normalizedAddress = walletAddress.toLowerCase();

        // Extract encrypted string if it's wrapped in an object
        let encryptedString: string;
        if (typeof encryptedData === 'string') {
            encryptedString = encryptedData;
        } else if (encryptedData && typeof encryptedData === 'object') {
            // Check if it's wrapped in pinataContent or similar
            if ('pinataContent' in encryptedData) {
                encryptedString = encryptedData.pinataContent;
            } else if ('data' in encryptedData) {
                encryptedString = encryptedData.data;
            } else {
                // Try to stringify and use as-is
                encryptedString = JSON.stringify(encryptedData);
            }
        } else {
            encryptedString = String(encryptedData);
        }

        // Generate key with normalized address
        const key = generateEncryptionKey(normalizedAddress, auditId);

        // Decrypt using AES
        const decrypted = CryptoJS.AES.decrypt(encryptedString, key);
        const decryptedString = decrypted.toString(CryptoJS.enc.Utf8);

        if (!decryptedString) {
            throw new Error('Decryption failed. Invalid key or corrupted data. Make sure you are using the same wallet that created this audit.');
        }

        // Try to parse as JSON, if fails return as string
        try {
            return JSON.parse(decryptedString);
        } catch {
            return decryptedString;
        }
    } catch (error: any) {
        throw new Error(`Failed to decrypt: ${error.message}`);
    }
}

/**
 * Verify hash matches the data
 * @param data The data to verify
 * @param hash The hash to compare against (bytes32 format)
 * @returns True if hash matches
 */
export function verifyHash(data: any, hash: string): boolean {
    const computedHash = hashJSONToBytes32(data);
    return computedHash.toLowerCase() === hash.toLowerCase();
}

