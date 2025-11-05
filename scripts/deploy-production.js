const { ethers } = require("hardhat");

async function main() {
    const [deployer] = await ethers.getSigners();

    console.log("Deploying contracts with the account:", deployer.address);

    const honeyTokenAddress = process.env.HONEY_TOKEN_ADDRESS;
    const gasServiceAddress = process.env.GAS_SERVICE_ADDRESS;
    const feeVaultAddress = process.env.FEE_VAULT_ADDRESS;
    const icaHubAddress = process.env.ICA_HUB_ADDRESS;

    if (!honeyTokenAddress || !gasServiceAddress || !feeVaultAddress || !icaHubAddress) {
        console.error("Please set the HONEY_TOKEN_ADDRESS, GAS_SERVICE_ADDRESS, FEE_VAULT_ADDRESS, and ICA_HUB_ADDRESS environment variables");
        process.exit(1);
    }

    const CartmanBridgeFactory = await ethers.getContractFactory("CartmanBridge");
    const bridge = await CartmanBridgeFactory.deploy(
        honeyTokenAddress,
        icaHubAddress,
        gasServiceAddress,
        feeVaultAddress
    );

    console.log("CartmanBridge deployed to:", await bridge.getAddress());
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
