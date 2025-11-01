// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../../contracts/CartmanBridge.sol";

contract MockIBCPrecompile is IBCPrecompile {
    function submitIBCPacket(bytes memory) external override {}
}
