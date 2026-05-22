# CartmanBridge Startup Status

## Current Verdict

CartmanBridge is a promising protocol-infrastructure prototype, not yet a production startup product. The repo has a coherent smart-contract thesis, a Hardhat test suite, mock integrations, and a deploy script. The next step is to convert it from prototype language into a credible audit-ready developer product.

## Product Category

CartmanBridge should be framed as cross-chain settlement infrastructure for Berachain-oriented applications.

Best initial category:

- Relayer reimbursement accounting
- IBC/ICA settlement control
- Protocol fee capture and fee-vault routing
- Governance-configurable economics
- Developer tooling for settlement-risk experiments

Avoid positioning it as:

- Guaranteed yield
- User-facing profit promise
- Mainnet-ready financial product
- Automated arbitrage system for public funds

## Target Users

1. Berachain builders who need IBC/ICA settlement primitives.
2. Protocol teams experimenting with relayer reimbursement economics.
3. Infrastructure operators who need cleaner gas-fee accounting.
4. Auditors and researchers evaluating bridge-settlement risk.

## Startup Wedge

The strongest wedge is not "a bridge." The strongest wedge is a settlement-accounting module for cross-chain protocol operators.

Practical launch line:

> CartmanBridge is an audit-track smart-contract module for Berachain settlement accounting, relayer reimbursement, and governance-controlled fee capture.

## MVP Definition

The repo reaches MVP status when all items below are complete:

- Local tests pass from a clean clone.
- CI compiles and tests the contracts on every pull request.
- Security policy and responsible disclosure policy exist.
- Threat model covers IBC packet validation, ICA authority, fee-vault failure, relayer payment, and governance compromise.
- Testnet deployment script is documented with exact required variables.
- README clearly states the contract is unaudited until third-party review is complete.
- No documentation makes investment, yield, or risk-free profit claims.
- Contract events are mapped to monitoring requirements.
- A public roadmap separates prototype, audit candidate, testnet, and production milestones.

## First Commercializable Offer

Offer CartmanBridge as a paid integration package for protocol teams:

1. Settlement accounting design review.
2. Custom relayer reimbursement policy implementation.
3. Berachain IBC/ICA testnet deployment support.
4. Monitoring dashboard specification.
5. Audit-prep package with threat model and invariant checklist.

## Monetization Hypotheses

- Integration fee for protocol teams.
- Audit-prep and security-hardening package.
- Hosted monitoring or analytics layer for settlement events.
- Protocol revenue share only after audit, governance review, and production hardening.

## Technical Gaps Blocking Startup-Ready Status

1. The IBC precompile address is hardcoded and should be validated against target-network documentation before deployment.
2. `execute_ica_governance` currently combines `onlyIbcModule` with an internal check against `ICA_HUB`, creating an authority mismatch that needs design clarification.
3. Mock token behavior is intentionally minimal and does not model balances, approvals, or ERC-20 failure modes.
4. Fee-vault behavior is mocked and should be represented by a real interface contract and failure tests.
5. `messageId` construction depends on timestamp and sender data; collision and replay assumptions should be documented and tested.
6. Packet decoding needs malformed-packet tests, short-payload tests, and adversarial payload tests.
7. No slippage, chain-finality, relayer griefing, or stuck-fee recovery model is documented yet.

## Launch Gates

### Gate 1: Prototype Credibility

- CI added.
- README de-risked.
- Security and audit docs added.
- Tests documented.

### Gate 2: Audit Candidate

- Threat model completed.
- Invariant tests added.
- Fuzzing or property tests added.
- Mock contracts made more realistic.
- Role and permission model cleaned up.

### Gate 3: Testnet Product

- Testnet addresses published.
- Monitoring dashboard spec created.
- Example deployment logs included.
- Integration guide added.

### Gate 4: Startup Launch

- Landing page.
- Demo video or transaction walkthrough.
- Audit report or public audit contest.
- Design partner pipeline.
- Clear pricing package for integration support.

## Recommended Next PRs

1. Fix authority model around `execute_ica_governance`.
2. Add malformed IBC packet tests.
3. Add realistic ERC-20 mock with balances, approvals, mint, burn, and transfer failure cases.
4. Add a deployment configuration validator.
5. Add event-monitoring documentation.
6. Add formal invariant checklist.
