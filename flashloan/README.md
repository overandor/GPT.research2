# Flashloan

This project provides a proof-of-concept implementation for wrapping standard LP tokens to make them flash-loanable.

## Security / Audit Status

**Proof-of-concept implementation and has not been audited. Use at your own risk.**

## Functionality

This project consists of two main components:

1.  **Smart Contracts:** A set of Solidity smart contracts that enable the wrapping of LP tokens and the execution of flash loans.
2.  **Python CLI Client:** A Python-based command-line interface for interacting with the smart contracts.

### Smart Contracts

*   `FlashLPWrapper.sol`: A wrapper that makes standard LP tokens flash-loanable.
*   `LPFlashLoaner.sol`: A contract to execute flash loans using the wrapped tokens.
*   `IFlashableLP.sol`: An interface for the flash-loanable LP tokens.
*   `IERC20.sol`: A standard ERC20 interface.

### Python CLI Client

The Python CLI client provides the following commands:

*   `wrap-lp`: Wraps an LP token to make it flash-loanable.
*   `flash-loan`: Executes a flash loan.
*   `get-balance`: Gets the balance of a token for a given owner.

## CLI Usage

### `wrap-lp`

Wraps a specified amount of an LP token.

```bash
python flashloan/cli.py wrap-lp --lp-token <LP_TOKEN_ADDRESS> --amount <AMOUNT>
```

### `flash-loan`

Executes a flash loan.

```bash
python flashloan/cli.py flash-loan --lp-token <FLASH_LP_TOKEN_ADDRESS> --executor <EXECUTOR_ADDRESS> --data <DATA>
```

### `get-balance`

Gets the balance of a token for a given owner.

```bash
python flashloan/cli.py get-balance --token <TOKEN_ADDRESS> --owner <OWNER_ADDRESS>
```
