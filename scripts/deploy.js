const { ethers } = require("hardhat");

async function main() {
    const [deployer] = await ethers.getSigners();

    console.log("Deploying contracts with the account:", deployer.address);

    const MockWrappedTokenFactory = await ethers.getContractFactory("MockWrappedToken");
    const honeyToken = await MockWrappedTokenFactory.deploy();

    const MockInterchainGasServiceFactory = await ethers.getContractFactory("MockInterchainGasService");
    const gasService = await MockInterchainGasServiceFactory.deploy();

    const MockFeeVaultFactory = await ethers.getContractFactory("MockFeeVault");
    const feeVault = await MockFeeVaultFactory.deploy();

    const CartmanBridgeFactory = await ethers.get_ContractFactory("CartmanBridge");
    const bridge = await CartmanBridgeFactory.deploy(
        await honeyToken.getAddress(),
        deployer.address, // Using deployer as the initial ICA_HUB
        await gasService.getAddress(),
        await feeVault.getAddress()
    );

    console.log("CartmanBridge deployed to:", await bridge.getAddress());
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
