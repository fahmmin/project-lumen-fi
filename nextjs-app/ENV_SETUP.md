# Environment Variables Setup

## Next.js App (.env.local)

Create a `.env.local` file in the root of `nextjs-app/` with the following variables:

```env
# Python Backend API URL
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:8000

# Pinata API Key (JWT) - Get from https://app.pinata.cloud/keys
NEXT_PUBLIC_PINATA_API_KEY=your_pinata_jwt_token_here

# Contract Address - Set after deploying the contract to Sepolia
NEXT_PUBLIC_CONTRACT_ADDRESS=0x...
```

## Hardhat Project (.env)

Create a `.env` file in the `hardhat/` directory with the following variables:

**Option 1: Full RPC URL (Recommended)**
```env
# Sepolia RPC URL (use Infura, Alchemy, or any Sepolia RPC endpoint)
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY
# OR
# SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY
# OR use public endpoint (may be rate-limited)
# SEPOLIA_RPC_URL=https://rpc.sepolia.org
```

**Option 2: Use Infura API Key**
```env
# If you only have Infura API key, set this instead
INFURA_API_KEY=your_infura_api_key_here
```

**Required:**
```env
# Private key of the account you want to deploy from (without 0x prefix)
PRIVATE_KEY=your_private_key_here
```

**Optional:**
```env
# Etherscan API key for contract verification
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

**Note:** If neither `SEPOLIA_RPC_URL` nor `INFURA_API_KEY` is set, the config will use the public RPC endpoint `https://rpc.sepolia.org` (may be rate-limited).

## Getting Your Pinata API Key

1. Go to [Pinata Dashboard](https://app.pinata.cloud/)
2. Navigate to API Keys section
3. Create a new JWT API key
4. Copy the JWT token and paste it in `.env.local` as `NEXT_PUBLIC_PINATA_API_KEY`

## Getting Sepolia Testnet Setup

### 1. Get Sepolia ETH

You'll need Sepolia ETH to deploy the contract and pay for gas:

- [Sepolia Faucet](https://sepoliafaucet.com/)
- [Alchemy Sepolia Faucet](https://sepoliafaucet.com/)
- [Infura Sepolia Faucet](https://www.infura.io/faucet/sepolia)

### 2. Get RPC URL

**Recommended:** Use a reliable RPC provider (Infura or Alchemy) to avoid timeout issues.

Choose one:

- **Infura** (Recommended): Sign up at [Infura](https://infura.io/), create a project, get your API key
- **Alchemy**: Sign up at [Alchemy](https://www.alchemy.com/), create an app, get your API key
- **Public RPC**: Use one of these (may be slower or rate-limited):
  - `https://rpc.sepolia.org`
  - `https://ethereum-sepolia-rpc.publicnode.com`
  - `https://sepolia.gateway.tenderly.co`

**Note:** If you experience timeout errors, use Infura or Alchemy instead of public RPCs.

### 3. Get Private Key

Export your private key from MetaMask:

1. Open MetaMask
2. Go to Account Details
3. Export Private Key (keep this secure!)

### 4. Deploy Contract

```bash
cd hardhat
npm install
npx hardhat run scripts/deploy.js --network sepolia
```

Copy the deployed contract address and add it to `.env.local` as `NEXT_PUBLIC_CONTRACT_ADDRESS`.

## MetaMask Configuration

The app will automatically connect to Sepolia testnet via MetaMask. Make sure:

1. MetaMask is installed
2. You have Sepolia testnet added (or it will prompt you to add it)
3. You have some Sepolia ETH for gas fees

## Security Notes

- **Never commit `.env` or `.env.local` files to git**
- Keep your private keys secure
- Use testnet accounts, not mainnet accounts
- The `NEXT_PUBLIC_` prefix makes variables available in the browser
