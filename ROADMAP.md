# CartmanBridge Roadmap

## Phase 0: Repository Credibility

Goal: make the repository understandable, testable, and safe to evaluate.

- Reposition README around audit-track protocol infrastructure.
- Add CI for install, compile, and test.
- Add security policy.
- Add audit-readiness checklist.
- Add startup-status document.
- Remove or qualify unsafe production/profit claims.

## Phase 1: Protocol Hardening

Goal: make the contract credible for external technical review.

- Resolve ICA/IBC authority ambiguity.
- Add nonce-based message IDs or a documented replay-protection mechanism.
- Add malformed packet tests.
- Add realistic ERC-20 mock behavior.
- Add fee-vault failure and native-transfer failure tests.
- Add fuzz/property testing for settlement math.
- Add Slither static-analysis workflow.
- Add test coverage reporting.

## Phase 2: Testnet Candidate

Goal: create a safe public testnet artifact.

- Add network config templates without private keys.
- Add testnet deployment guide.
- Publish sample deployment logs.
- Publish testnet addresses.
- Add event-monitoring spec.
- Add demo transaction walkthrough.
- Add integration guide for protocol teams.

## Phase 3: Audit Candidate

Goal: make the repo ready for a third-party audit or contest.

- Freeze audited commit hash.
- Publish final threat model.
- Publish invariants and assumptions.
- Include all external dependency addresses.
- Include privileged role-management plan.
- Include emergency response plan.
- Open public issue tracker for audit findings.

## Phase 4: Startup Launch

Goal: convert technical artifact into a productized startup asset.

- Create landing page.
- Create technical whitepaper.
- Create developer integration package.
- Recruit 3-5 design partners.
- Package paid integration/audit-prep service.
- Add dashboard specification for event monitoring.
- Publish clear risk disclosures.

## Backlog

- Governance timelock support.
- Emergency pause pattern, if compatible with protocol goals.
- Fee-vault interface hardening.
- Relayer registry and reputation layer.
- Route-level fee quoting.
- Settlement analytics dashboard.
- Public SDK for integration tests.
- Berachain-specific deployment templates.
