// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// --- Imports (Conceptual Interfaces) ---

interface IInterchainGasService {
    function payNativeGasForContractCall(address sender, uint16 destinationChainId, uint256 gasLimit) external payable;
}

interface IBCPrecompile {
    function submitIBCPacket(bytes memory packet) external;
}

interface IWrappedToken {
    function mint(address to, uint256 amount) external;
    function burn(address from, uint256 amount) external;
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
}

interface IFeeVault {
    function depositProfit() external payable;
}

// --- Custom Errors ---
error InvalidIbcModule();
error FeeAlreadyClaimedOrInvalid();
error ZeroGasPayment();
error IcaExecutionFailed();
error Unauthorized();
error FeeShareTooHigh();
error InvalidPacketType();
error ProfitFloorBreached();
error AutoCompoundFailed();
error SettlementMathError();
error RefundTransferFailed();

// --- Packet Type Discriminators ---
bytes4 constant PACKET_TYPE_WHONEY_REDEMPTION = 0x1BCC0DE1;
bytes4 constant PACKET_TYPE_GENERIC_MESSAGE  = 0x1BCC0DE2;

// --- Imports (from OpenZeppelin) ---
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title CartmanBridge
 * @author Your Name
 * @notice EVM-Native Deep Integration for Berachain, managing IBC, ICA, and Guaranteed Profit (GP) Extraction.
 */
contract CartmanBridge is ReentrancyGuard {

    // --- State Variables ---

    /// @notice The address of the wHONEY token contract.
    address public immutable WHONEY_TOKEN;
    /// @notice The address of the Interchain Accounts (ICA) Hub.
    address public immutable ICA_HUB;
    /// @notice The address of the auto-compounding fee vault.
    address public immutable FEE_VAULT;

    /// @notice The address of the IBC precompile contract.
    address public constant IBC_PRECOMPILE_ADDRESS = address(uint160(0x80081BC));
    /// @notice The address of the IBC module handler.
    address public IBC_MODULE_HANDLER;

    /// @notice The interchain gas service contract.
    IInterchainGasService public immutable gasService;

    /// @notice The fee share percentage for the protocol.
    uint256 public cartmanFeeShare;
    /// @notice The minimum profit floor in basis points.
    uint256 public minProfitBps;

    /// @notice A mapping from message ID to locked fees.
    mapping(bytes32 => uint256) public lockedFees;
    /// @notice A mapping from message ID to the gas arbitrage reserve.
    mapping(bytes32 => uint256) public gasArbReserve;

    // --- Events ---

    event CrossChainMessageSent(uint16 indexed destinationChain, bytes32 indexed messageId, address indexed sender);
    event AssetMinted(address indexed user, address indexed token, uint256 amount);
    event IcaGovernanceExecuted(address indexed ica, bytes32 indexed payloadHash);
    event FeeShareUpdated(uint256 newFeeShare);
    event GasFeeRefunded(bytes32 indexed messageId, address indexed recipient, uint256 amount);
    event MinProfitBpsUpdated(uint256 newProfitBps);
    event RelayerReimbursed(bytes32 indexed messageId, address indexed relayer, uint256 reimbursement, uint256 effectiveCut);
    event GasArbCaptured(bytes32 indexed messageId, uint256 arbAmount);

    /**
     * @notice Constructs the CartmanBridge contract.
     * @param _honey The address of the wHONEY token.
     * @param _icaHub The address of the ICA Hub.
     * @param _gasService The address of the interchain gas service.
     * @param _feeVault The address of the fee vault.
     */
    constructor(address _honey, address _icaHub, address _gasService, address _feeVault) {
        WHONEY_TOKEN = _honey;
        ICA_HUB = _icaHub;
        gasService = IInterchainGasService(_gasService);
        FEE_VAULT = _feeVault;
        cartmanFeeShare = 5; // Initialize with a 5% fee
        minProfitBps = 300; // Initialize with a 3% profit floor
        IBC_MODULE_HANDLER = msg.sender; // Set the deployer as the initial handler
    }

    /**
     * @notice Sets the IBC module handler address.
     * @param newHandler The address of the new IBC module handler.
     */
    function setIbcModuleHandler(address newHandler) external onlyIcaHub {
        IBC_MODULE_HANDLER = newHandler;
    }

    // --- Modifiers ---

    /**
     * @dev Throws if called by any account other than the IBC module handler.
     */
    modifier onlyIbcModule() {
        if (msg.sender != IBC_MODULE_HANDLER) revert InvalidIbcModule();
        _;
    }

    /**
     * @dev Throws if called by any account other than the ICA Hub.
     */
    modifier onlyIcaHub() {
        if (msg.sender != ICA_HUB) revert Unauthorized();
        _;
    }

    /**
     * @dev Ensures that a transaction does not breach the minimum profit floor.
     * @param amountToWithdraw The amount to be withdrawn from the contract.
     */
    modifier profitGuard(uint256 amountToWithdraw) {
        uint256 requiredFloor = (address(this).balance * minProfitBps) / 10_000;
        if (address(this).balance < amountToWithdraw + requiredFloor) revert ProfitFloorBreached();
        _;
    }

    // --- IBC Integration ---

    /**
     * @notice Sends a burn transaction to the IBC precompile.
     * @param amount The amount of wHONEY to burn.
     * @param destinationIBCChannel The destination IBC channel.
     */
    function sendBurnToIBC(uint256 amount, string memory destinationIBCChannel) external {
        IWrappedToken(WHONEY_TOKEN).burn(msg.sender, amount);
        bytes memory payloadData = abi.encode(amount, msg.sender);
        bytes memory payload = abi.encodePacked(PACKET_TYPE_WHONEY_REDEMPTION, payloadData);
        IBCPrecompile(IBC_PRECOMPILE_ADDRESS).submitIBCPacket(abi.encode(destinationIBCChannel, payload));
        emit CrossChainMessageSent(888, keccak256(payload), msg.sender);
    }

    /**
     * @notice Handles incoming IBC packets.
     * @param verifiedPayload The verified IBC packet payload.
     */
    function receive_ibc_packet(bytes memory verifiedPayload) external onlyIbcModule {
        bytes4 packetType;
        bytes memory payloadData = verifiedPayload;

        assembly { packetType := mload(add(payloadData, 32)) }

        bytes memory slicedPayload = _slice(payloadData, 4, payloadData.length - 4);

        if (packetType == PACKET_TYPE_WHONEY_REDEMPTION) {
            (uint256 amount, address recipient) = abi.decode(slicedPayload, (uint256, address));
            IWrappedToken(WHONEY_TOKEN).mint(recipient, amount);
            emit AssetMinted(recipient, WHONEY_TOKEN, amount);
        } else if (packetType == PACKET_TYPE_GENERIC_MESSAGE) {
            (address token, uint256 amount, address recipient, ) = abi.decode(slicedPayload, (address, uint256, address, bytes));
            IWrappedToken(token).mint(recipient, amount);
            emit AssetMinted(recipient, token, amount);
        } else {
            revert InvalidPacketType();
        }
    }

    // --- ICA Governance ---

    /**
     * @notice Executes a series of EVM transactions via the ICA Hub.
     * @param evmTxPayloads An array of EVM transaction payloads.
     */
    function execute_ica_governance(bytes[] memory evmTxPayloads) external onlyIbcModule {
        if (msg.sender != ICA_HUB) revert Unauthorized();
        for (uint i = 0; i < evmTxPayloads.length; i++) {
            (bool success,) = ICA_HUB.call(evmTxPayloads[i]);
            if (!success) revert IcaExecutionFailed();
        }
    }

    /**
     * @notice Updates the minimum profit floor.
     * @param newProfitBps The new minimum profit floor in basis points.
     */
    function updateMinProfitBps(uint256 newProfitBps) external onlyIcaHub {
        if (newProfitBps > 1000) revert FeeShareTooHigh(); // Max 10%
        minProfitBps = newProfitBps;
        emit MinProfitBpsUpdated(newProfitBps);
    }

    // --- IGP Settlement ---

    /**
     * @notice Pays for interchain gas.
     * @param destinationChain The destination chain ID.
     * @param gasLimit The gas limit for the transaction.
     * @return messageId The ID of the message.
     */
    function payInterchainGas(uint16 destinationChain, uint256 gasLimit) public payable returns (bytes32 messageId) {
        if (msg.value == 0) revert ZeroGasPayment();

        messageId = keccak256(abi.encode(msg.sender, block.timestamp, destinationChain));
        lockedFees[messageId] = msg.value;

        gasService.payNativeGasForContractCall{value: msg.value}(
            msg.sender,
            destinationChain,
            gasLimit
        );

        emit CrossChainMessageSent(destinationChain, messageId, msg.sender);
    }

    /**
     * @notice Reimburses a relayer for gas costs and auto-compounds the profit.
     * @param relayer The address of the relayer.
     * @param messageId The ID of the message.
     * @param actualGasCost The actual gas cost of the transaction.
     */
    function reimburseRelayer(address relayer, bytes32 messageId, uint256 actualGasCost)
        external
        onlyIbcModule
        profitGuard(0)
        nonReentrant
    {
        uint256 totalFee = lockedFees[messageId];
        if (totalFee == 0) revert FeeAlreadyClaimedOrInvalid();

        uint256 initialCartmanCut = (totalFee * cartmanFeeShare) / 100;
        uint256 initialRelayerPayment = totalFee - initialCartmanCut;

        uint256 gasSpreadArb = 0;
        if (initialRelayerPayment > actualGasCost) {
            uint256 delta = initialRelayerPayment - actualGasCost;
            gasSpreadArb = delta / 2;
            gasArbReserve[messageId] = gasSpreadArb;
        }

        uint256 reimbursement = actualGasCost;

        uint256 effectiveCut = enforceProfitFloor(totalFee, reimbursement);

        uint256 finalRelayerPayment = totalFee - effectiveCut;
        uint256 finalCartmanCut = effectiveCut;

        if (finalRelayerPayment + finalCartmanCut != totalFee) revert SettlementMathError();

        delete lockedFees[messageId];

        (bool success1,) = relayer.call{value: finalRelayerPayment}("");
        if (!success1) revert("Relayer reimbursement failed.");

        (bool success2,) = FEE_VAULT.call{value: finalCartmanCut}("");
        if (!success2) revert AutoCompoundFailed();

        emit RelayerReimbursed(messageId, relayer, finalRelayerPayment, finalCartmanCut);
        if (gasSpreadArb > 0) emit GasArbCaptured(messageId, gasSpreadArb);
    }

    /**
     * @notice Enforces the guaranteed profit floor.
     * @param totalFee The total fee paid for the transaction.
     * @param reimbursement The amount to be reimbursed.
     * @return effectiveCut The effective cut for the protocol.
     */
    function enforceProfitFloor(uint256 totalFee, uint256 reimbursement) internal view returns (uint256 effectiveCut) {
        uint256 requiredProfit = (totalFee * minProfitBps) / 10_000;
        uint256 currentCut = totalFee - reimbursement;

        if (currentCut < requiredProfit) {
            effectiveCut = requiredProfit;
        } else {
            effectiveCut = currentCut;
        }

        if (effectiveCut > totalFee) return totalFee;

        return effectiveCut;
    }

    /**
     * @notice Updates the Cartman fee share.
     * @param newFeeShare The new fee share percentage.
     */
    function updateCartmanFeeShare(uint256 newFeeShare) external onlyIcaHub {
        if (newFeeShare > 20) revert FeeShareTooHigh(); // Max 20%
        cartmanFeeShare = newFeeShare;
        emit FeeShareUpdated(newFeeShare);
    }

    /**
     * @notice Refunds a locked gas fee.
     * @param messageId The ID of the message.
     * @param recipient The recipient of the refund.
     */
    function refundLockedGasFee(bytes32 messageId, address payable recipient) external onlyIcaHub profitGuard(lockedFees[messageId]) nonReentrant {
        uint256 amount = lockedFees[messageId];
        if (amount == 0) revert FeeAlreadyClaimedOrInvalid();

        delete lockedFees[messageId];

        (bool success,) = recipient.call{value: amount}("");
        if (!success) revert RefundTransferFailed();

        emit GasFeeRefunded(messageId, recipient, amount);
    }

    /**
     * @dev Slices a bytes array.
     * @param bs The bytes array to slice.
     * @param start The starting index.
     * @param len The length of the slice.
     * @return A new bytes array containing the slice.
     */
    function _slice(bytes memory bs, uint start, uint len) internal pure returns (bytes memory) {
        bytes memory t = new bytes(len);
        for (uint i = 0; i < len; i++) {
            t[i] = bs[start + i];
        }
        return t;
    }

    receive() external payable {}
}
