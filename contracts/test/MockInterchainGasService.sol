// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../../contracts/CartmanBridge.sol";

contract MockInterchainGasService is IInterchainGasService {
    function payNativeGasForContractCall(
        address,
        uint16,
        uint256
    ) external payable override {}
}
