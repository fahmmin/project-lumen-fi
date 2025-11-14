# Encryption/Decryption Flow Explanation

## Overview

This document explains how audit reports are encrypted, stored, and decrypted in the system.

## Complete Flow

### 1. **Storage Flow (Store Page)**

```
User Input (Audit Report JSON)
    ↓
[Step 1: Encryption]
    - Input: Original audit report JSON + Wallet Address + Audit ID
    - Process: 
      * Normalize wallet address to lowercase
      * Generate encryption key: SHA256(lowercase_address + auditId)
      * Encrypt JSON using AES-256 with the generated key
    - Output: Encrypted string (ciphertext)
    ↓
[Step 2: Upload to IPFS]
    - Input: Encrypted string
    - Process:
      * Upload encrypted string to Pinata IPFS
      * Pinata wraps it: { pinataContent: "encrypted_string", ... }
    - Output: IPFS hash/URL
    ↓
[Step 3: Hash Encrypted Data]
    - Input: Encrypted string (same as Step 1 output)
    - Process:
      * Compute SHA-256 hash of encrypted string
      * Convert to bytes32 format (0x-prefixed)
    - Output: bytes32 hash
    ↓
[Step 4: Store on Blockchain]
    - Input: Hash + IPFS URL + Audit ID
    - Process:
      * Call smart contract: storeAudit(hash, ipfsUrl, auditId)
      * Transaction signed by wallet
    - Output: Transaction receipt, audit stored on-chain
```

### 2. **Retrieval/Decryption Flow (View Page)**

```
Load Audits from Blockchain
    ↓
[Step 1: Fetch from IPFS]
    - Input: IPFS URL from blockchain
    - Process:
      * Fetch data from IPFS gateway
      * Handle multiple gateways (Pinata, public IPFS)
      * Extract encrypted string from response
        - If wrapped: extract pinataContent
        - If direct: use as-is
    - Output: Encrypted string
    ↓
[Step 2: Verify Creator]
    - Input: Current wallet address + storedBy address from blockchain
    - Process:
      * Compare addresses (case-insensitive)
      * Only proceed if match
    - Output: Authorization granted/denied
    ↓
[Step 3: Decryption]
    - Input: Encrypted string + Wallet Address + Audit ID
    - Process:
      * Normalize wallet address to lowercase
      * Generate same encryption key: SHA256(lowercase_address + auditId)
      * Decrypt using AES-256
    - Output: Original audit report JSON
    ↓
[Step 4: Hash Verification]
    - Input: Encrypted string + Hash from blockchain
    - Process:
      * Re-compute hash of encrypted string
      * Compare with stored hash
    - Output: Verification result (pass/fail)
    ↓
[Step 5: Display]
    - Input: Decrypted JSON
    - Process: Display formatted audit report
    - Output: User sees original audit data
```

## Key Points

### Encryption Key Generation

```javascript
// Key is derived from:
key = SHA256(lowercase(walletAddress) + auditId)

// Example:
// walletAddress = "0xAA7429cF1D6cdA01e7Ac3A472b88caB5140EF995"
// auditId = "audit_123"
// key = SHA256("0xaa7429cf1d6cda01e7ac3a472b88cab5140ef995-audit_123")
```

**Important**: Wallet addresses are normalized to lowercase to ensure consistency, as Ethereum addresses can be in mixed case.

### Data Structure on IPFS

When uploaded to Pinata:
```json
{
  "pinataContent": "U2FsdGVkX1...encrypted_string...",
  "pinataMetadata": {
    "name": "audit_123_encrypted.json"
  }
}
```

When fetched, we extract `pinataContent` to get the actual encrypted string.

### Security Features

1. **Access Control**: Only the wallet that created the audit can decrypt it
   - Encryption key requires the exact wallet address
   - Even if someone has the IPFS link, they cannot decrypt without the wallet

2. **Integrity Verification**: Hash verification ensures data hasn't been tampered
   - Hash is stored on blockchain (immutable)
   - Can verify encrypted data matches the hash

3. **Privacy**: Original data is never stored on blockchain
   - Only hash (one-way) is stored
   - Encrypted data on IPFS requires key to decrypt

## Troubleshooting

### "Failed to fetch from IPFS"
- **Cause**: IPFS gateway might be down or CORS issue
- **Solution**: System tries multiple gateways automatically
- **Check**: Verify IPFS URL is correct, try accessing directly in browser

### "Decryption failed"
- **Cause**: Wrong wallet address or audit ID
- **Solution**: 
  - Ensure you're using the same wallet that created the audit
  - Verify audit ID matches exactly
  - Check that wallet address is correct (case-insensitive matching)

### "Hash verification failed"
- **Cause**: Data on IPFS doesn't match the hash on blockchain
- **Solution**: 
  - Data may have been corrupted
  - IPFS gateway might be serving wrong data
  - Try different IPFS gateway

## Example Flow

**Storing:**
```
Original: {"audit_id": "audit_123", "status": "pass"}
Wallet: 0xAA7429cF1D6cdA01e7Ac3A472b88caB5140EF995
Audit ID: audit_123

→ Encrypt → "U2FsdGVkX1+vupppZksvRf5pq5g5XkFy..."
→ Upload to IPFS → QmXxxx...
→ Hash → 0xabc123...
→ Store on-chain
```

**Retrieving:**
```
From blockchain: hash=0xabc123, ipfs=QmXxxx, storedBy=0xAA74...

→ Fetch from IPFS → "U2FsdGVkX1+vupppZksvRf5pq5g5XkFy..."
→ Verify wallet matches → ✓
→ Decrypt → {"audit_id": "audit_123", "status": "pass"}
→ Verify hash → ✓
→ Display
```

