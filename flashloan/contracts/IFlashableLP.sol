// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IFlashableLP
 * @dev Interface for a flash-loanable LP token.
 */
interface IFlashableLP {
    /**
     * @dev Executes a flash loan.
     * @param executor The address of the contract that will execute the flash loan logic.
     * @param data Arbitrary data to be passed to the executor.
     */
    function flashLP(address executor, bytes calldata data) external;
}
