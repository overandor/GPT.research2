const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CartmanBridge", function () {
    let deployer, relayer, user, icaHub, ibcModule;

    let bridge, honeyToken, gasService, feeVault;

    beforeEach(async function () {
        [deployer, relayer, user, icaHub, ibcModule] = await ethers.getSigners();

        const MockWrappedTokenFactory = await ethers.getContractFactory("MockWrappedToken", deployer);
        honeyToken = await MockWrappedTokenFactory.deploy();

        const MockInterchainGasServiceFactory = await ethers.getContractFactory("MockInterchainGasService", deployer);
        gasService = await MockInterchainGasServiceFactory.deploy();

        const MockFeeVaultFactory = await ethers.getContractFactory("MockFeeVault", deployer);
        feeVault = await MockFeeVaultFactory.deploy();

        const CartmanBridgeFactory = await ethers.getContractFactory("CartmanBridge");
        bridge = await CartmanBridgeFactory.deploy(
            await honeyToken.getAddress(),
            icaHub.address,
            await gasService.getAddress(),
            await feeVault.getAddress()
        );

        // Natively fund the bridge for tests
        await deployer.sendTransaction({
            to: await bridge.getAddress(),
            value: ethers.parseEther("10"),
        });

        // Set the IBC module handler to the correct address
        await bridge.connect(icaHub).setIbcModuleHandler(ibcModule.address);
    });

    describe("Deployment and Initial State", function () {
        it("Should set the correct initial values", async function () {
            expect(await bridge.WHONEY_TOKEN()).to.equal(await honeyToken.getAddress());
            expect(await bridge.ICA_HUB()).to.equal(icaHub.address);
            expect(await bridge.gasService()).to.equal(await gasService.getAddress());
            expect(await bridge.FEE_VAULT()).to.equal(await feeVault.getAddress());
            expect(await bridge.cartmanFeeShare()).to.equal(5);
            expect(await bridge.minProfitBps()).to.equal(300);
        });
    });

    describe("IGP Settlement: payInterchainGas", function () {
        it("Should lock fees and emit a CrossChainMessageSent event", async function () {
            const fee = ethers.parseEther("0.1");
            await expect(bridge.connect(user).payInterchainGas(1, 200000, { value: fee }))
                .to.emit(bridge, "CrossChainMessageSent");
        });

        it("Should revert if no fee is paid", async function () {
            await expect(
                bridge.connect(user).payInterchainGas(1, 200000, { value: 0 })
            ).to.be.revertedWithCustomError(bridge, "ZeroGasPayment");
        });
    });

    describe("IGP Settlement: reimburseRelayer", function () {
        let messageId;
        const totalFee = ethers.parseEther("1");

        beforeEach(async function () {
            const tx = await bridge.connect(user).payInterchainGas(1, 200000, { value: totalFee });
            const receipt = await tx.wait();
            const event = bridge.interface.parseLog(receipt.logs[0]);
            messageId = event.args.messageId;
        });

        it("Should correctly reimburse the relayer and send profit to the vault", async function () {
            const actualGasCost = ethers.parseEther("0.8");
            const initialVaultBalance = await ethers.provider.getBalance(await feeVault.getAddress());

            await expect(bridge.connect(ibcModule).reimburseRelayer(relayer.address, messageId, actualGasCost))
                .to.emit(bridge, "RelayerReimbursed");

            const finalVaultBalance = await ethers.provider.getBalance(await feeVault.getAddress());
            expect(finalVaultBalance - initialVaultBalance).to.equal(ethers.parseEther("0.2"));
        });

        it("Should enforce the minimum profit floor", async function () {
            const actualGasCost = ethers.parseEther("0.98");
            const initialVaultBalance = await ethers.provider.getBalance(await feeVault.getAddress());

            await bridge.connect(ibcModule).reimburseRelayer(relayer.address, messageId, actualGasCost);

            const finalVaultBalance = await ethers.provider.getBalance(await feeVault.getAddress());
            expect(finalVaultBalance - initialVaultBalance).to.equal(ethers.parseEther("0.03"));
        });
    });

    describe("ICA Governance", function () {
        it("Should allow the ICA hub to update the minimum profit", async function () {
            const newMinProfit = 500;
            await expect(bridge.connect(icaHub).updateMinProfitBps(newMinProfit))
                .to.emit(bridge, "MinProfitBpsUpdated")
                .withArgs(newMinProfit);
            expect(await bridge.minProfitBps()).to.equal(newMinProfit);
        });

        it("Should prevent non-ICA hub from updating the minimum profit", async function () {
            await expect(
                bridge.connect(user).updateMinProfitBps(500)
            ).to.be.revertedWithCustomError(bridge, "Unauthorized");
        });

        it("Should allow the ICA hub to update the fee share", async function () {
            const newFeeShare = 10;
            await expect(bridge.connect(icaHub).updateCartmanFeeShare(newFeeShare))
                .to.emit(bridge, "FeeShareUpdated")
                .withArgs(newFeeShare);
            expect(await bridge.cartmanFeeShare()).to.equal(newFeeShare);
        });

        it("Should prevent non-ICA hub from updating the fee share", async function () {
            await expect(
                bridge.connect(user).updateCartmanFeeShare(10)
            ).to.be.revertedWithCustomError(bridge, "Unauthorized");
        });

        it("Should revert if the new fee share is too high", async function () {
            await expect(
                bridge.connect(icaHub).updateCartmanFeeShare(21)
            ).to.be.revertedWithCustomError(bridge, "FeeShareTooHigh");
        });
    });

    describe("Refunds", function () {
        let messageId;
        const totalFee = ethers.parseEther("1");

        beforeEach(async function () {
            const tx = await bridge.connect(user).payInterchainGas(1, 200000, { value: totalFee });
            const receipt = await tx.wait();
            const event = bridge.interface.parseLog(receipt.logs[0]);
            messageId = event.args.messageId;
        });

        it("Should allow the ICA hub to refund a locked fee", async function () {
            const initialUserBalance = await ethers.provider.getBalance(user.address);

            await expect(bridge.connect(icaHub).refundLockedGasFee(messageId, user.address))
                .to.emit(bridge, "GasFeeRefunded");

            const finalUserBalance = await ethers.provider.getBalance(user.address);
            expect(finalUserBalance).to.be.gt(initialUserBalance);
        });

        it("Should prevent non-ICA hub from refunding a fee", async function () {
            await expect(
                bridge.connect(user).refundLockedGasFee(messageId, user.address)
            ).to.be.revertedWithCustomError(bridge, "Unauthorized");
        });
    });
});
