# Troubleshooting Deployment Issues

## Headers Timeout Error

If you see `HeadersTimeoutError` or `Headers Timeout Error`, it means the RPC endpoint is not responding in time.

### Solutions:

1. **Use a more reliable RPC endpoint** (Recommended)

   Update your `hardhat/.env` file with one of these:

   **Option A: Infura (Free tier available)**
   ```env
   SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY
   ```

   **Option B: Alchemy (Free tier available)**
   ```env
   SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY
   ```

   **Option C: Public RPC endpoints (may be slower)**
   ```env
   # Try these alternatives:
   SEPOLIA_RPC_URL=https://ethereum-sepolia-rpc.publicnode.com
   # OR
   SEPOLIA_RPC_URL=https://sepolia.gateway.tenderly.co
   # OR
   SEPOLIA_RPC_URL=https://rpc.sepolia.org
   ```

2. **Check your internet connection**

   Make sure you have a stable internet connection.

3. **Increase timeout (already configured)**

   The Hardhat config already has a 120-second timeout. If it still times out, the RPC endpoint is likely down or overloaded.

4. **Retry the deployment**

   Sometimes RPC endpoints have temporary issues. Try again after a few minutes.

## Getting RPC API Keys

### Infura (Recommended)

1. Go to [Infura](https://infura.io/)
2. Sign up for a free account
3. Create a new project
4. Select "Sepolia" network
5. Copy your API key
6. Use: `SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_API_KEY`

### Alchemy

1. Go to [Alchemy](https://www.alchemy.com/)
2. Sign up for a free account
3. Create a new app
4. Select "Ethereum" and "Sepolia" network
5. Copy your API key
6. Use: `SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY`

## Other Common Issues

### "PRIVATE_KEY is not set"

Make sure you have a `.env` file in the `hardhat/` directory with:
```env
PRIVATE_KEY=your_private_key_without_0x_prefix
```

### "Account has no ETH"

You need Sepolia testnet ETH. Get it from:
- [Sepolia Faucet](https://sepoliafaucet.com/)
- [Alchemy Sepolia Faucet](https://sepoliafaucet.com/)
- [Infura Sepolia Faucet](https://www.infura.io/faucet/sepolia)

### "Invalid JSON-RPC response"

This usually means:
- The RPC URL is incorrect
- The API key is invalid
- The endpoint is down

Double-check your `.env` file and try a different RPC endpoint.

## Testing RPC Connection

You can test if your RPC endpoint is working:

```bash
curl -X POST https://sepolia.infura.io/v3/YOUR_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

If you get a response with a block number, the RPC is working.

