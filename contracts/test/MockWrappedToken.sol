// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../../contracts/CartmanBridge.sol";

contract MockWrappedToken is IWrappedToken {
    function mint(address, uint256) external override {}

    function burn(address, uint256) external override {}

    function transferFrom(
        address,
        address,
        uint256
    ) external override returns (bool) {
        return true;
    }
}
