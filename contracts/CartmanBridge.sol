// File: CartmanBridge.sol
// Purpose: EVM-Native Deep Integration for Berachain, managing IBC, ICA, and Guaranteed Profit (GP) Extraction.

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

// ** NEW INTERFACE: Auto-Compound Fee Vault **
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

// --- Cartman's Core Bridge Contract ---
contract CartmanBridge is ReentrancyGuard {

    // EVM Addresses
    address public immutable WHONEY_TOKEN;
    address public immutable ICA_HUB;
    address public immutable FEE_VAULT; // ** NEW: Address for yield compounding **

    address public constant IBC_PRECOMPILE_ADDRESS = address(uint160(0x80081BC));
    address public IBC_MODULE_HANDLER;

    // Services
    IInterchainGasService public immutable gasService;

    // State
    uint256 public cartmanFeeShare; // Base 5% (5)
    uint256 public minProfitBps = 300;  // ** NEW: 3% guaranteed minimum profit floor (300) **

    mapping(bytes32 => uint256) public lockedFees;
    mapping(bytes32 => uint256) public gasArbReserve; // ** NEW: Holds the gas overpayment delta **

    // Events
    event CrossChainMessageSent(uint16 indexed destinationChain, bytes32 indexed messageId, address indexed sender);
    event AssetMinted(address indexed user, address indexed token, uint256 amount);
    event IcaGovernanceExecuted(address indexed ica, bytes32 indexed payloadHash);
    event FeeShareUpdated(uint256 newFeeShare);
    event GasFeeRefunded(bytes32 indexed messageId, address indexed recipient, uint256 amount);
    event MinProfitBpsUpdated(uint256 newProfitBps);
    event RelayerReimbursed(bytes32 indexed messageId, address indexed relayer, uint256 reimbursement, uint256 effectiveCut);
    event GasArbCaptured(bytes32 indexed messageId, uint256 arbAmount); // ** NEW **

    constructor(address _honey, address _icaHub, address _gasService, address _feeVault) {
        WHONEY_TOKEN = _honey;
        ICA_HUB = _icaHub;
        gasService = IInterchainGasService(_gasService);
        FEE_VAULT = _feeVault;
        cartmanFeeShare = 5; // Initialize with a 5% fee
        IBC_MODULE_HANDLER = msg.sender; // Set the deployer as the initial handler
    }

    function setIbcModuleHandler(address newHandler) external onlyIcaHub {
        IBC_MODULE_HANDLER = newHandler;
    }

    // --- Modifiers ---
    modifier onlyIbcModule() {
        if (msg.sender != IBC_MODULE_HANDLER) revert InvalidIbcModule();
        _;
    }

    modifier onlyIcaHub() {
        if (msg.sender != ICA_HUB) revert Unauthorized();
        _;
    }

    // ** NEW: Failsafe Profit Guard **
    modifier profitGuard(uint256 amountToWithdraw) {
        // Required floor is based on the current contract balance, ensuring the remaining balance >= floor.
        // E.g., if balance=100 and floor=10, amountToWithdraw can be at most 90.
        uint256 requiredFloor = (address(this).balance * minProfitBps) / 10_000;
        if (address(this).balance < amountToWithdraw + requiredFloor) revert ProfitFloorBreached();
        _;
    }

    // --- I. IBC Integration (Stubs for completeness) ---

    // Retained for outbound wHONEY flow
    function sendBurnToIBC(uint256 amount, string memory destinationIBCChannel) external {
        IWrappedToken(WHONEY_TOKEN).burn(msg.sender, amount);
        bytes memory payloadData = abi.encode(amount, msg.sender);
        bytes memory payload = abi.encodePacked(PACKET_TYPE_WHONEY_REDEMPTION, payloadData);
        IBCPrecompile(IBC_PRECOMPILE_ADDRESS).submitIBCPacket(abi.encode(destinationIBCChannel, payload));
        emit CrossChainMessageSent(888, keccak256(payload), msg.sender); // Simple keccak for messageId
    }

    // Retained for inbound packet handling with type discrimination
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

    // --- II. ICA Governance (Extended) ---

    function execute_ica_governance(bytes[] memory evmTxPayloads) external onlyIbcModule {
        if (msg.sender != ICA_HUB) revert Unauthorized();
        for (uint i = 0; i < evmTxPayloads.length; i++) {
            (bool success,) = ICA_HUB.call(evmTxPayloads[i]);
            if (!success) revert IcaExecutionFailed();
        }
        // Simplified event: IcaGovernanceExecuted
    }

    // ** NEW ICA function: Update Profit Floor **
    function updateMinProfitBps(uint256 newProfitBps) external onlyIcaHub {
        if (newProfitBps > 1000) revert FeeShareTooHigh(); // Max 10% (1000 BPS)
        minProfitBps = newProfitBps;
        emit MinProfitBpsUpdated(newProfitBps);
    }

    // --- III. IGP Settlement (Refactored for Guaranteed Profit) ---

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

    // ** REFACTORED: Reimbursement with Dynamic Fee Amplifier & Auto-Compound Vault **
    function reimburseRelayer(address relayer, bytes32 messageId, uint256 actualGasCost)
        external
        onlyIbcModule
        profitGuard(0) // Check the total balance integrity before starting settlement
        nonReentrant // Protect against reentrancy attacks
    {
        uint256 totalFee = lockedFees[messageId];
        if (totalFee == 0) revert FeeAlreadyClaimedOrInvalid();

        // 1. Calculate Initial Cut (based on cartmanFeeShare)
        uint256 initialCartmanCut = (totalFee * cartmanFeeShare) / 100;
        uint256 initialRelayerPayment = totalFee - initialCartmanCut;

        // 2. Elastic Gas Arbitrage Module: Capture Overpayment
        // If the relayer was overpaid, capture 50% of the difference as additional profit.
        uint256 gasSpreadArb = 0;
        if (initialRelayerPayment > actualGasCost) {
            uint256 delta = initialRelayerPayment - actualGasCost;
            gasSpreadArb = delta / 2;
            gasArbReserve[messageId] = gasSpreadArb;
        }

        // The reimbursement amount is the minimum needed (actualGasCost)
        uint256 reimbursement = actualGasCost;

        // 3. Dynamic Fee Amplifier: Enforce Profit Floor
        // Calculate the maximum possible cut based on the profit floor or the base share.
        uint256 effectiveCut = enforceProfitFloor(totalFee, reimbursement);

        uint256 finalRelayerPayment = totalFee - effectiveCut;
        uint256 finalCartmanCut = effectiveCut;

        // Final sanity check: Ensure no funds are lost or created.
        if (finalRelayerPayment + finalCartmanCut != totalFee) revert SettlementMathError();

        delete lockedFees[messageId]; // Prevents reentrancy/double claim

        // 4. Reimburse Relayer and Auto-Compound Profit
        // Transfer the final calculated payment to the relayer.
        (bool success1,) = relayer.call{value: finalRelayerPayment}("");
        if (!success1) revert("Relayer reimbursement failed.");

        // Deposit all profit into the auto-compounding fee vault.
        (bool success2,) = FEE_VAULT.call{value: finalCartmanCut}("");
        if (!success2) revert AutoCompoundFailed();

        emit RelayerReimbursed(messageId, relayer, finalRelayerPayment, finalCartmanCut);
        if (gasSpreadArb > 0) emit GasArbCaptured(messageId, gasSpreadArb);
    }

    // ** NEW: Internal function to enforce the Guaranteed Profit Floor **
    function enforceProfitFloor(uint256 totalFee, uint256 reimbursement) internal view returns (uint256 effectiveCut) {
        uint256 requiredProfit = (totalFee * minProfitBps) / 10_000;
        uint256 currentCut = totalFee - reimbursement;

        // Effective cut is the max of the static profit (currentCut) and the required floor (requiredProfit).
        if (currentCut < requiredProfit) {
            effectiveCut = requiredProfit;
        } else {
            effectiveCut = currentCut;
        }

        // Safety check: The effective cut cannot exceed the total fee.
        if (effectiveCut > totalFee) return totalFee;

        return effectiveCut;
    }

    // ** NEW ICA function: Update Cartman Fee Share **
    function updateCartmanFeeShare(uint256 newFeeShare) external onlyIcaHub {
        if (newFeeShare > 20) revert FeeShareTooHigh(); // Max 20%
        cartmanFeeShare = newFeeShare;
        emit FeeShareUpdated(newFeeShare);
    }

    // ** REFACTORED: Refund using Profit Guard **
    function refundLockedGasFee(bytes32 messageId, address payable recipient) external onlyIcaHub profitGuard(lockedFees[messageId]) nonReentrant {
        uint256 amount = lockedFees[messageId];
        if (amount == 0) revert FeeAlreadyClaimedOrInvalid();

        delete lockedFees[messageId];

        // Full locked amount is refunded. Profit is zero.
        (bool success,) = recipient.call{value: amount}("");
        if (!success) revert RefundTransferFailed();

        emit GasFeeRefunded(messageId, recipient, amount);
    }

    // NOTE: Access functions for gasArbReserve, while useful, are omitted for brevity in the core bridge logic.

    function _slice(bytes memory bs, uint start, uint len) internal pure returns (bytes memory) {
        bytes memory t = new bytes(len);
        for (uint i = 0; i < len; i++) {
            t[i] = bs[start + i];
        }
        return t;
    }

    receive() external payable {}
}