// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../contracts/FlashLPWrapper.sol";
import "../contracts/LPFlashLoaner.sol";
import "../contracts/IERC20.sol";

contract TestFlashLoan {
    // Mock ERC20 token for testing
    class MockERC20 is ERC20 {
        constructor(string memory name, string memory symbol) ERC20(name, symbol) {}
        function mint(address to, uint256 amount) external {
            _mint(to, amount);
        }
    }

    // Mock Executor for testing flash loans
    class MockExecutor {
        bytes public data;
        IERC20 public underlying;
        FlashLPWrapper public wrapper;

        constructor(IERC20 _underlying, FlashLPWrapper _wrapper) {
            underlying = _underlying;
            wrapper = _wrapper;
        }

        function execute(bytes calldata _data) external {
            data = _data;
            uint256 balance = underlying.balanceOf(address(this));
            uint256 fee = (balance * wrapper.FLASH_FEE()) / 10000;
            underlying.approve(address(wrapper), balance + fee);
            // Repay the loan + fee
            underlying.transfer(address(wrapper), balance + fee);
        }
    }

    // Test deposit and withdraw
    function testDepositAndWithdraw() external {
        MockERC20 underlying = new MockERC20("Underlying", "UL");
        FlashLPWrapper wrapper = new FlashLPWrapper(underlying);

        underlying.mint(address(this), 1000);
        underlying.approve(address(wrapper), 1000);

        wrapper.deposit(1000);
        require(wrapper.balanceOf(address(this)) == 1000, "Deposit failed");

        wrapper.withdraw(1000);
        require(wrapper.balanceOf(address(this)) == 0, "Withdraw failed");
        require(underlying.balanceOf(address(this)) == 1000, "Withdraw failed");
    }

    // Test flash loan
    function testFlashLoan() external {
        MockERC20 underlying = new MockERC20("Underlying", "UL");
        FlashLPWrapper wrapper = new FlashLPWrapper(underlying);
        // The owner of LPFlashLoaner is this contract
        LPFlashLoaner loaner = new LPFlashLoaner(address(wrapper));
        MockExecutor executor = new MockExecutor(underlying, wrapper);

        // Fund the wrapper with some tokens
        underlying.mint(address(wrapper), 1000);
        // Fund the executor with enough to pay the fee
        uint256 fee = (1000 * wrapper.FLASH_FEE()) / 10000;
        underlying.mint(address(executor), fee);


        bytes memory data = abi.encodeWithSignature("execute(bytes)", "test data");
        loaner.executeFlashLoan(address(executor), data);

        require(underlying.balanceOf(address(wrapper)) == 1000 + fee, "Flash loan failed");
    }
}
