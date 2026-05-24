# Security Policy

## Status

CartmanBridge is currently an unaudited prototype. It should not be deployed with real user funds until the audit and launch gates are complete.

## Supported Versions

The only supported branch for security review is the active audit/readiness branch or the repository default branch after merge.

## Reporting a Vulnerability

If you discover a vulnerability, do not open a public GitHub issue with exploit details.

Report privately to the repository owner through GitHub or a designated security contact once one is published. Include:

- A concise vulnerability summary.
- Affected contract, function, and commit hash.
- Preconditions required for exploitation.
- Minimal proof of concept, if safe to share privately.
- Potential impact.
- Suggested mitigation, if known.

## Scope

In scope:

- Smart-contract authorization failures.
- IBC packet replay or decoding vulnerabilities.
- Unauthorized mint/burn flows.
- Relayer reimbursement theft or double-claim conditions.
- Locked-fee lifecycle bugs.
- Reentrancy through native transfers or external calls.
- Governance parameter bypasses.
- Fee-vault failure modes.

Out of scope until explicitly launched:

- Issues requiring real mainnet deployment, because the project is not approved for mainnet funds.
- Social engineering.
- Denial-of-service against GitHub, npm, or unrelated infrastructure.
- Speculative financial-loss claims without a concrete technical exploit path.

## Disclosure Expectations

Please allow reasonable time for triage and remediation before public disclosure. Critical issues should remain private until a fix is available or a safe mitigation notice is published.

## Launch Safety Rule

No documentation, demo, or deployment should represent CartmanBridge as audited, risk-free, or profit-guaranteeing until those claims are independently supported.
