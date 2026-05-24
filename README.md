# CartmanBridge

CartmanBridge is a research-stage Solidity protocol prototype for Berachain-oriented cross-chain settlement. It explores Inter-Blockchain Communication (IBC), Interchain Accounts (ICA), interchain gas accounting, protocol fee capture, and a configurable profit-floor settlement policy.

> Status: prototype / audit candidate. Do not deploy with real user funds until the audit checklist, integration checklist, and deployment controls in this repository are complete.

## Product Thesis

Cross-chain applications often leak value through relayer uncertainty, gas overpayment, settlement latency, and weak fee-accounting controls. CartmanBridge packages those concerns into a single smart-contract module that can be tested, governed, monitored, and eventually integrated into Berachain-native infrastructure.

## Core Capabilities

- IBC packet handling for wHONEY redemption and generic wrapped-token mint flows.
- ICA-gated governance controls for fee-share and profit-floor configuration.
- Interchain gas fee locking, relayer reimbursement, and surplus capture accounting.
- Fee-vault forwarding for protocol revenue accumulation.
- Hardhat test suite with mocks for external gas, fee-vault, token, and IBC dependencies.
- Deployment script that expects production addresses to be supplied through environment variables.

## What "Profit Floor" Means

The protocol-level profit floor is a settlement-accounting rule that reserves a minimum protocol cut from a paid gas fee before final relayer reimbursement is calculated. It is not a user investment guarantee, not a yield guarantee, and not a representation that every route or deployment will be profitable.

## Repository Structure

```text
contracts/CartmanBridge.sol              Core contract
contracts/test/                          Mock contracts for local tests
scripts/deploy-production.js             Deployment script using external addresses
test/CartmanBridge.js                    Hardhat test suite
TESTING.md                               Test summary and coverage areas
STARTUP_STATUS.md                        Startup-readiness plan and launch gates
AUDIT_READINESS.md                       Security review checklist
SECURITY.md                              Disclosure and security policy
ROADMAP.md                               Product roadmap
.github/workflows/ci.yml                 GitHub Actions CI workflow
```

## Quick Start

```sh
npm ci
npx hardhat compile
npx hardhat test
```

## Deployment

Set production addresses explicitly before deployment:

```sh
export HONEY_TOKEN_ADDRESS=<your-honey-token-address>
export GAS_SERVICE_ADDRESS=<your-gas-service-address>
export FEE_VAULT_ADDRESS=<your-fee-vault-address>
export ICA_HUB_ADDRESS=<your-ica-hub-address>
npx hardhat run scripts/deploy-production.js --network <your-network>
```

Before any mainnet or user-funds deployment, complete the following gates:

1. Independent smart-contract audit.
2. Formal threat model covering IBC packet validation, ICA authority, relayer economics, and fee-vault failure modes.
3. Public testnet deployment with documented addresses and monitored events.
4. Multisig ownership and emergency response procedure.
5. Reproducible CI passing on the target branch.
6. Launch disclosure that clearly states protocol risks and non-guarantees.

## Startup Packaging

CartmanBridge should be positioned as a protocol-infrastructure primitive, not a consumer yield product. The strongest initial wedge is a developer-facing Berachain settlement-risk toolkit: fee accounting, gas reimbursement, relayer surplus capture, and governance-controlled economic parameters.

See `STARTUP_STATUS.md`, `AUDIT_READINESS.md`, and `ROADMAP.md` for the startup conversion plan.

## License

MIT, unless superseded by a repository-level license file.
