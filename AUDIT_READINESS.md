# CartmanBridge Audit Readiness

This document converts CartmanBridge from a prototype into an audit-track smart-contract project. It is not an audit report.

## Audit Status

Current status: unaudited prototype.

Do not deploy with real user funds until an independent third-party audit or public security contest is complete and all critical/high findings are resolved.

## System Components

- `CartmanBridge`: core contract for IBC packet handling, gas-fee locking, relayer reimbursement, fee capture, and governance-controlled parameters.
- `IWrappedToken`: token interface used for mint/burn operations.
- `IInterchainGasService`: external gas service interface used for interchain gas payment.
- `IBCPrecompile`: precompile interface for packet submission.
- `IFeeVault`: fee-vault interface for profit routing.
- Test mocks under `contracts/test/` for isolated local testing.

## Trust Boundaries

### Trusted / Privileged

- `ICA_HUB`: can update fee parameters and refund locked gas.
- `IBC_MODULE_HANDLER`: can call packet receive and relayer reimbursement functions.
- `FEE_VAULT`: receives protocol fees and must safely handle native token transfers.

### Untrusted / External

- User-supplied IBC payloads.
- Relayer address inputs.
- External gas service behavior.
- Wrapped token behavior.
- Fee-vault call behavior.
- Native token transfer behavior.

## High-Risk Areas

1. Packet decoding and packet-type discrimination.
2. Role authorization between `ICA_HUB` and `IBC_MODULE_HANDLER`.
3. Native token settlement math and profit-floor enforcement.
4. Relayer reimbursement accounting.
5. Fee-vault transfer failure handling.
6. Locked-fee lifecycle and stuck-fee recovery.
7. Message ID uniqueness and replay protection.
8. Hardcoded precompile address and network assumptions.
9. External token mint/burn trust assumptions.
10. Governance parameter limits.

## Known Design Questions

- Should `execute_ica_governance` be callable by the IBC module handler, the ICA hub, or a separate governance executor? The current implementation uses `onlyIbcModule` and then checks `msg.sender != ICA_HUB`, which implies an impossible or highly constrained caller model unless the two roles are the same address.
- Should packet payloads include source chain, channel, nonce, proof metadata, or replay protection identifiers?
- Should `messageId` include a nonce instead of timestamp-derived entropy?
- Should failed fee-vault deposits leave claimable balances rather than reverting the whole reimbursement?
- Should relayer reimbursement cap actual gas cost using an oracle, quoted gas price, or max reimbursement policy?

## Required Tests Before Audit

### Authorization

- Non-authorized callers rejected for all privileged functions.
- Role transfer behavior tested.
- ICA hub and IBC module role separation tested.
- Governance edge cases at max/min allowed values.

### IBC Payloads

- Invalid packet type.
- Empty payload.
- Payload shorter than 4 bytes.
- Malformed ABI-encoded payload.
- Valid packet with unexpected extra bytes.
- Replay attempt with identical payload.

### Settlement Math

- Actual gas cost equals total fee.
- Actual gas cost greater than total fee.
- Actual gas cost lower than total fee.
- Profit floor greater than available spread.
- Fee share at 0%, default, and max.
- Rounding behavior for small values.

### External Calls

- Relayer transfer failure.
- Fee-vault transfer failure.
- Wrapped token mint failure.
- Wrapped token burn failure.
- Gas service revert.
- Reentrancy attempt through relayer and fee-vault fallback.

### Invariants

- A message ID cannot be reimbursed twice.
- A message ID cannot be refunded after reimbursement.
- A message ID cannot be reimbursed after refund.
- Protocol fee plus relayer payment equals total locked fee for every successful reimbursement.
- Locked fee is deleted before external transfers.
- Governance updates remain within configured bounds.

## Recommended Tooling

- Slither static analysis.
- Foundry fuzzing or Echidna property tests.
- Hardhat gas reporter.
- Solidity coverage.
- OpenZeppelin Defender or equivalent monitoring for privileged actions.

## Audit Package Checklist

Before submitting to auditors, include:

- Final commit hash.
- Deployment assumptions and target chain IDs.
- External contract addresses or mocks.
- Threat model.
- Test coverage report.
- Invariant list.
- Known limitations.
- Privileged role management plan.
- Emergency pause/incident plan if added.

## Severity Priorities

Critical:

- Unauthorized minting or burning.
- Locked fee theft or double claim.
- Governance bypass.
- Packet replay leading to asset inflation.

High:

- Stuck funds with no recovery path.
- Incorrect relayer reimbursement.
- Fee-vault failure causing systemic liveness failure.
- Role ambiguity causing governance deadlock.

Medium:

- Excessive rounding loss.
- Incomplete event coverage.
- Poor deployment validation.

Low:

- Documentation inconsistency.
- Naming ambiguity.
- Missing developer ergonomics.
