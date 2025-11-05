// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./IFlashableLP.sol";
import "./utils/Ownable.sol";

/**
 * @title LPFlashLoaner
 * @dev A contract to execute flash loans using wrapped LP tokens.
 * @notice This is a proof-of-concept implementation and has not been audited.
 * Use at your own risk.
 */
contract LPFlashLoaner is Ownable {
    IFlashableLP public immutable lpToken;

    constructor(address _lpToken) {
        lpToken = IFlashableLP(_lpToken);
    }

    /**
     * @dev Executes a flash loan by delegating the call to the lpToken.
     * @param executor The address of the contract that will execute the flash loan logic.
     * @param data Arbitrary data to be passed to the executor.
     */
    function executeFlashLoan(address executor, bytes calldata data) external onlyOwner {
        lpToken.flashLP(executor, data);
    }
}
