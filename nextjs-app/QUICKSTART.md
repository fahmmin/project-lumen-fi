# Quick Start Guide

## Prerequisites

1. **Node.js 18+** installed
2. **MetaMask** browser extension installed
3. **Python backend** running on `http://localhost:8000`
4. **Pinata API key** (JWT) from [Pinata Dashboard](https://app.pinata.cloud/keys)
5. **Sepolia testnet ETH** for gas fees

## Setup Steps

### 1. Install Dependencies

```bash
cd nextjs-app
npm install
```

### 2. Set Up Environment Variables

Create `.env.local` file in `nextjs-app/`:

```env
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:8000
NEXT_PUBLIC_PINATA_API_KEY=your_pinata_jwt_here
NEXT_PUBLIC_CONTRACT_ADDRESS=
```

See [ENV_SETUP.md](./ENV_SETUP.md) for detailed instructions.

### 3. Set Up Hardhat for Sepolia

In `hardhat/` directory, create `.env`:

```env
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY
PRIVATE_KEY=your_private_key_here
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

Install Hardhat dependencies:

```bash
cd hardhat
npm install
```

### 4. Deploy Smart Contract to Sepolia

```bash
cd hardhat
npx hardhat run scripts/deploy.js --network sepolia
```

Copy the contract address from the output and add it to `.env.local`:

```env
NEXT_PUBLIC_CONTRACT_ADDRESS=0x...
```

### 5. Configure MetaMask

1. Open MetaMask
2. Make sure Sepolia testnet is added (MetaMask usually has it by default)
3. Switch to Sepolia testnet
4. Get Sepolia ETH from a faucet if needed

### 5. Start the Application

```bash
cd nextjs-app
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage Workflow

### Step 1: Upload Document to Pinata

1. Go to `/upload`
2. Make sure `NEXT_PUBLIC_PINATA_API_KEY` is set in `.env.local` (restart dev server if you just added it)
3. Select a file
4. Click "Upload to Pinata IPFS"
5. Copy the IPFS hash/URL

### Step 2: Run Audit

1. Go to `/audit`
2. Fill in invoice data:
   - Vendor (required)
   - Date (required)
   - Amount (required)
   - Tax, Category, Invoice Number (optional)
3. Click "Run Full Audit"
4. Wait for results
5. Copy the full audit report JSON

### Step 3: Store on Blockchain

1. Go to `/store`
2. Connect MetaMask wallet
3. Enter contract address (or it will use from .env.local)
4. Paste audit report JSON
5. Click "Hash Audit Report"
6. Enter Pinata link and Audit ID
7. Click "Store Audit on Blockchain"
8. Confirm transaction in MetaMask

## Troubleshooting

### MetaMask Connection Issues

- Make sure MetaMask is unlocked
- Check that you're on the correct network (Hardhat Local)
- Try refreshing the page

### Contract Not Found

- Verify contract address in `.env.local`
- Make sure Hardhat node is running
- Redeploy the contract if needed

### Pinata Upload Fails

- Verify your JWT API key is correct
- Check your Pinata account has available storage
- Ensure file size is within limits

### Backend API Errors

- Verify Python backend is running on port 8000
- Check `NEXT_PUBLIC_PYTHON_API_URL` in `.env.local`
- Test backend health: `curl http://localhost:8000/health`

## Next Steps

- Review the full [README.md](./README.md) for detailed documentation
- Check [ENV_SETUP.md](./ENV_SETUP.md) for environment variable details
- Explore the codebase to understand the architecture

