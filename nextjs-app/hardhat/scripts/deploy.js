const hre = require("hardhat");

async function main() {
    const network = hre.network.name;
    console.log(`Deploying AuditStorage contract to ${network}...`);

    // Validate environment variables for Sepolia
    if (network === "sepolia") {
        if (!process.env.PRIVATE_KEY) {
            throw new Error("PRIVATE_KEY is not set in .env file. Please add your private key.");
        }
        if (!process.env.SEPOLIA_RPC_URL && !process.env.INFURA_API_KEY) {
            console.warn("⚠️  Warning: Using public RPC endpoint (https://rpc.sepolia.org). For better reliability, set SEPOLIA_RPC_URL or INFURA_API_KEY in .env");
            console.warn("   Alternative public RPCs you can try:");
            console.warn("   - https://ethereum-sepolia-rpc.publicnode.com");
            console.warn("   - https://sepolia.gateway.tenderly.co");
        }
    }

    console.log("Connecting to network...");
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying with account:", deployer.address);

    try {
        const balance = await hre.ethers.provider.getBalance(deployer.address);
        console.log("Account balance:", hre.ethers.formatEther(balance), "ETH");

        if (network === "sepolia" && balance === 0n) {
            throw new Error("Account has no ETH. Please fund your account with Sepolia ETH from a faucet.");
        }
    } catch (error) {
        if (error.message.includes("timeout") || error.message.includes("Headers Timeout")) {
            throw new Error(
                "RPC endpoint timeout. Try:\n" +
                "1. Use a different RPC endpoint (Infura, Alchemy, or another public RPC)\n" +
                "2. Check your internet connection\n" +
                "3. Set SEPOLIA_RPC_URL in .env to a more reliable endpoint"
            );
        }
        throw error;
    }

    const AuditStorage = await hre.ethers.getContractFactory("AuditStorage");
    const auditStorage = await AuditStorage.deploy();

    await auditStorage.waitForDeployment();

    const address = await auditStorage.getAddress();
    console.log("\n✅ AuditStorage deployed to:", address);
    console.log("\nCopy this address to your .env.local file:");
    console.log(`NEXT_PUBLIC_CONTRACT_ADDRESS=${address}`);

    if (network === "sepolia") {
        console.log("\n⏳ Waiting for block confirmations...");
        await auditStorage.deploymentTransaction().wait(5);
        console.log("✅ Contract verified on Sepolia");
        console.log(`\nView on Etherscan: https://sepolia.etherscan.io/address/${address}`);
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });

