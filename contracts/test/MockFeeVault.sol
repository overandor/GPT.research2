// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../../contracts/CartmanBridge.sol";

contract MockFeeVault is IFeeVault {
    function depositProfit() external payable override {}

    receive() external payable {}
}
