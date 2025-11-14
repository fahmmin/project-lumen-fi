# Web3 Audit Platform

A Next.js application that integrates with the Python FastAPI backend to run audits, upload documents to Pinata IPFS, and store audit report hashes on the blockchain.

## Features

- 📤 **Pinata IPFS Upload**: Upload documents to decentralized IPFS storage
- 🔍 **AI-Powered Audits**: Run comprehensive audits via Python backend
- ⛓️ **Blockchain Storage**: Store audit report hashes on-chain for immutability
- 🔐 **MetaMask Integration**: Connect wallet and interact with smart contracts

## Prerequisites

- Node.js 18+ and npm
- MetaMask browser extension
- Python backend running on `http://localhost:8000`
- Pinata API key (JWT) - will be read from environment
- Sepolia testnet ETH for gas fees

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   
   Create `.env.local` in the root of `nextjs-app/`:
   ```env
   NEXT_PUBLIC_PYTHON_API_URL=http://localhost:8000
   NEXT_PUBLIC_PINATA_API_KEY=your_pinata_jwt_here
   NEXT_PUBLIC_CONTRACT_ADDRESS=
   ```
   
   See [ENV_SETUP.md](./ENV_SETUP.md) for detailed instructions.

3. **Set up Hardhat (for contract deployment):**
   ```bash
   cd hardhat
   npm install
   ```

4. **Configure Hardhat for Sepolia:**
   
   Create `.env` in the `hardhat/` directory:
   ```env
   SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY
   PRIVATE_KEY=your_private_key_here
   ETHERSCAN_API_KEY=your_etherscan_api_key_here
   ```

5. **Deploy the contract to Sepolia:**
   ```bash
   cd hardhat
   npx hardhat run scripts/deploy.js --network sepolia
   ```
   Copy the deployed contract address to `.env.local` as `NEXT_PUBLIC_CONTRACT_ADDRESS`

6. **Run the development server:**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
nextjs-app/
├── app/                    # Next.js pages
│   ├── page.tsx           # Home page
│   ├── upload/page.tsx    # Pinata upload page
│   ├── audit/page.tsx     # Audit execution page
│   └── store/page.tsx     # On-chain storage page
├── components/            # Reusable components
│   ├── WalletConnect.tsx
│   ├── LoadingSpinner.tsx
│   └── Notification.tsx
├── services/              # Service layers
│   ├── api.ts            # Python backend API client
│   ├── pinata.ts         # Pinata IPFS service
│   ├── web3.ts           # Web3/contract service
│   └── crypto.ts         # Hashing utilities
└── hardhat/              # Hardhat project
    ├── contracts/
    │   └── AuditStorage.sol
    └── scripts/
        └── deploy.js
```

## Usage

### 1. Upload Document to Pinata

1. Navigate to `/upload`
2. Make sure `NEXT_PUBLIC_PINATA_API_KEY` is set in `.env.local`
3. Select a file to upload
4. Click "Upload to Pinata IPFS"
5. Copy the IPFS hash/URL for later use

### 2. Run Audit

1. Navigate to `/audit`
2. Fill in the invoice data form
3. Click "Run Full Audit"
4. Review the audit results
5. Copy the audit report JSON for hashing

### 3. Store on Blockchain

1. Navigate to `/store`
2. Connect your MetaMask wallet (make sure you're on Sepolia testnet)
3. The contract address will be loaded from `.env.local` or you can enter it manually
4. Paste the audit report JSON and click "Hash Audit Report"
5. Enter the Pinata link and audit ID
6. Click "Store Audit on Blockchain"
7. Confirm the transaction in MetaMask

## Smart Contract

The `AuditStorage` contract stores:
- Audit report hash (bytes32)
- Pinata IPFS link (string)
- Audit ID (string)
- Timestamp and sender address

### Contract Functions

- `storeAudit(bytes32 hash, string pinataLink, string auditId)`: Store an audit record
- `getAudit(uint256 index)`: Get audit by index
- `getAuditById(string auditId)`: Get audit by ID
- `getAuditCount()`: Get total number of audits
- `isHashStored(bytes32 hash)`: Check if hash exists

## Development

### Build for production

```bash
npm run build
npm start
```

### Hardhat Commands

```bash
cd hardhat

# Compile contracts
npm run compile

# Deploy to local network
npm run deploy

# Start local node
npm run node
```

## Troubleshooting

- **MetaMask not connecting**: Make sure MetaMask is installed, unlocked, and on Sepolia testnet
- **Contract not found**: Verify the contract address in `.env.local` and that it's deployed to Sepolia
- **Pinata upload fails**: Check that `NEXT_PUBLIC_PINATA_API_KEY` is set in `.env.local` and restart the dev server
- **Backend API errors**: Ensure the Python backend is running on the correct port
- **Insufficient funds**: Make sure you have Sepolia ETH in your MetaMask wallet for gas fees
- **Wrong network**: The app expects Sepolia testnet (Chain ID: 11155111)

## License

MIT
