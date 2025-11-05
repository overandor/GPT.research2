// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./IERC20.sol";
import "./IFlashableLP.sol";
import "./utils/ReentrancyGuard.sol";
import "./utils/ERC20.sol";

contract FlashLPWrapper is ERC20, IFlashableLP, ReentrancyGuard {
    IERC20 public underlying;
    uint256 public constant FLASH_FEE = 10; // 0.1%

    constructor(IERC20 _underlying) ERC20("Flash LP Token", "fLP") {
        underlying = _underlying;
    }

    function deposit(uint256 amount) external {
        underlying.transferFrom(msg.sender, address(this), amount);
        _mint(msg.sender, amount);
    }

    function withdraw(uint256 amount) external {
        _burn(msg.sender, amount);
        underlying.transfer(msg.sender, amount);
    }

    function flashLP(address executor, bytes calldata data) external nonReentrant {
        uint256 balanceBefore = underlying.balanceOf(address(this));

        underlying.transfer(executor, balanceBefore);

        (bool success, ) = executor.call(data);
        require(success, "FlashLPWrapper: Executor call failed");

        uint256 balanceAfter = underlying.balanceOf(address(this));
        uint256 fee = (balanceBefore * FLASH_FEE) / 10000;
        require(balanceAfter >= balanceBefore + fee, "FlashLPWrapper: Flash loan not repaid");
    }
}
