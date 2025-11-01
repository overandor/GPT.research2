# CartmanBridge

## Overview

CartmanBridge is a Solidity-based smart contract designed for deep integration with the Berachain ecosystem. It manages Inter-Blockchain Communication (IBC), Interchain Accounts (ICA), and a unique "Guaranteed Profit" (GP) extraction mechanism.

### Key Features

*   **Guaranteed Profit Settlement:** A novel settlement system that ensures a minimum profit margin on all cross-chain transactions.
*   **Dynamic Fee Management:** A flexible fee structure that can be adjusted via on-chain governance.
*   **Auto-Compounding Vault:** A dedicated vault that automatically compounds profits, maximizing returns for the protocol.
*   **Robust Security:** Built-in security features, including reentrancy guards and access control, to protect against common vulnerabilities.

## Installation

To set up a local development environment, you'll need Node.js and npm installed.

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    ```
2.  **Navigate to the project directory:**
    ```sh
    cd CartmanBridge
    ```
3.  **Install the dependencies:**
    ```sh
    npm install
    ```

## Testing

The project includes a comprehensive test suite to ensure the contract's correctness and security. To run the tests, execute the following command:

```sh
npx hardhat test
```

## Deployment

The deployment process is streamlined with a Hardhat script. To deploy the contract, follow these steps:

1.  **Configure your deployment network:**
    Update the `hardhat.config.js` file with the desired network configuration, including the network URL and private key.
2.  **Run the deployment script:**
    ```sh
    npx hardhat run scripts/deploy.js --network <your-network>
    ```

### Post-Deployment

After deployment, it is crucial to perform the following steps to ensure the contract's security and proper functioning:

1.  **Transfer Ownership:**
    The `ICA_HUB` and `IBC_MODULE_HANDLER` roles are critical to the contract's governance. Transfer these roles to the appropriate multisig or DAO contracts.
2.  **Security Audit:**
    Conduct a thorough security audit with a reputable third-party firm to identify and address any potential vulnerabilities.
3.  **Monitoring:**
    Set up a monitoring system to track key contract events and metrics, such as `RelayerReimbursed` and `GasArbCaptured`, to ensure the contract is operating as expected.
