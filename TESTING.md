# CartmanBridge Testing

This document provides a comprehensive overview of the testing process for the `CartmanBridge` smart contract. The test suite is designed to ensure the contract's correctness, security, and adherence to the specified requirements.

## Test Suite Summary

The test suite is written in JavaScript using the Hardhat testing framework and consists of 15 tests that cover all aspects of the contract's functionality. The tests are organized into the following categories:

*   **Deployment and Initial State:** Verifies that the contract is deployed with the correct initial values.
*   **IGP Settlement:** Verifies the "Guaranteed Profit" settlement logic, including the `payInterchainGas` and `reimburseRelayer` functions.
*   **ICA Governance:** Verifies the on-chain governance mechanisms for updating the contract's parameters.
*   **Refunds:** Verifies the functionality of the `refundLockedGasFee` function.
*   **IBC Integration:** Verifies the contract's ability to handle incoming IBC packets.

### Testing "Systems" with Mock Contracts

The `CartmanBridge` contract interacts with several external "systems," including an Interchain Gas Service, an IBC Precompile, and a Wrapped Token. To ensure the isolated and predictable testing of the `CartmanBridge`'s logic, these external systems were simulated using mock contracts.

The mock contracts are located in the `contracts/test` directory and are designed to mimic the behavior of the real systems in a controlled environment. This approach allows for the thorough testing of the `CartmanBridge`'s functionality without relying on external dependencies.

## Test Results

The test suite was executed using the Hardhat testing framework, and all 15 tests passed successfully. The following is a summary of the test results:

```
  CartmanBridge
    Deployment and Initial State
      ✔ Should set the correct initial values
    IGP Settlement: payInterchainGas
      ✔ Should lock fees and emit a CrossChainMessageSent event
      ✔ Should revert if no fee is paid
    IGP Settlement: reimburseRelayer
      ✔ Should correctly reimburse the relayer, capture gas arbitrage, and send profit to the vault
      ✔ Should enforce the minimum profit floor when gas costs are high
      ✔ Should correctly reimburse when gas cost is very high, respecting profit floor
    ICA Governance
      ✔ Should allow the ICA hub to update the minimum profit
      ✔ Should prevent non-ICA hub from updating the minimum profit
      ✔ Should allow the ICA hub to update the fee share
      ✔ Should prevent non-ICA hub from updating the fee share
      ✔ Should revert if the new fee share is too high
    Refunds
      ✔ Should allow the ICA hub to refund a locked fee
      ✔ Should prevent non-ICA hub from refunding a fee
    IBC Integration
      ✔ Should handle wHONEY redemption packets (52ms)
      ✔ Should handle generic message packets (61ms)


  15 passing (1s)
```
