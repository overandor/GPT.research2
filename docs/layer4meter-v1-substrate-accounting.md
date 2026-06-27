# Layer4Meter V1: Substrate Accounting for AI-Native Mac Work

## Mature Framing

Layer4Meter is not a hidden-compute detector.

It is a substrate accountant.

Correct product claim:

> Layer4Meter measures unattributed substrate work behind AI-native production and binds that work to a verified artifact receipt.

Wrong product claim:

> Layer4Meter discovers hidden magic compute.

The product is not a monitor. It is a receipt machine.

Activity Monitor answers:

```text
Which app used CPU?
```

Layer4Meter answers:

```text
What machine work was consumed to produce this artifact?
How much of that work was useful?
What proofs exist?
What value came out per substrate unit?
```

## Core Economic Primitive

```text
LCI_raw = measured substrate activity

LCI_adjusted =
  AgentWorkload_LCI
- IdleBaseline_LCI
- HumanBaseline_LCI

ValuePerLCI =
  VerifiedArtifactValue / LCI_adjusted
```

This gives AI-native production a denominator.

Without the denominator, “AI made this” is just a claim.

With the denominator, it becomes measurable production accounting.

## Verified Artifact Value

`VerifiedArtifactValue` cannot be invented.

Allowed sources:

```text
invoice paid
contract value
accepted deliverable
passed tests
merged PR
signed client approval
market-listed asset
valuation packet with explicit assumptions
```

If none exists:

```text
VerifiedArtifactValue = unverified
```

Layer4Meter may still compute substrate cost, proof density, and artifact readiness, but it must not claim verified economic value.

## V1 Scope

Layer4Meter V1 should be boring, local, measurable, and hard to attack.

Capture:

- project folder file changes
- Git diffs
- terminal/build/test events
- lightweight process/resource samples
- checkpoints before and after agent work
- hashes and Merkle root

Avoid in V1:

- Endpoint Security dependency
- kernel-level monitoring
- full screen recording
- zero-knowledge proofs
- claims of hidden compute
- revenue claims without verified artifact value
- automatic valuation claims

## macOS Instrumentation Map

### Visual Checkpoints

Use ScreenCaptureKit or a lower-fidelity screenshot/checkpoint fallback for user-authorized visual state.

V1 rule:

- checkpoint only
- no continuous screen recording by default
- redact or hash sensitive visual artifacts

### File Changes

Use FSEvents for project-directory change detection.

V1 rule:

- watch only project folders
- hash contents after change events
- store path hashes when paths are sensitive
- separate project deltas from background churn

### Process / Command Events

Do not require Endpoint Security in V1.

V1 process evidence can come from:

- terminal wrapper
- shell history capture where permitted
- build logs
- test logs
- process snapshots
- Git hooks
- explicit command receipts

Endpoint Security belongs in V2/V3 because it may require entitlement and elevated deployment complexity.

### Power / Performance Samples

MetricKit is useful for diagnostics and performance reporting, but it should not be the V1 live telemetry backbone.

V1 should use lightweight sampling:

- CPU sample
- memory pressure sample
- disk write sample
- network byte sample
- process count sample
- retry/stuck-loop timing

MetricKit can supplement reports later.

### Time / Snapshot Anchors

Use snapshots as temporal anchors, not permanent storage.

V1 rule:

- record before/after checkpoint hashes
- record file existence proof
- optionally reference local snapshots when available
- never claim retention beyond tested system behavior

## `.l4receipt` V1 Format

```text
receipt.l4receipt
├── manifest.json
├── events.sqlite
├── files.jsonl
├── git.jsonl
├── process.jsonl
├── power.jsonl
├── checkpoints.jsonl
├── claims.jsonl
├── shard_hashes.json
├── merkle_root.txt
└── report.md
```

Screenshots, PDFs, Endpoint Security, notarization, ZK, and signed external verification come later.

## V1 Claims

V1 should prove:

- session started
- session ended
- project path existed
- watched files changed
- file hashes changed
- Git state changed
- commands/build/test events were recorded
- artifact existed at output path
- tests passed or failed
- Merkle root binds all shards
- report was generated

V1 should not claim:

- exact energy attribution
- complete system-level process visibility
- complete user activity visibility
- causation of every background event
- verified market value unless value source is attached
- ZK proof unless an actual proof/verifier exists

## Command Shape

```text
layer4 start --project ./AgentLedger
layer4 checkpoint before-agent
layer4 command -- "npm test"
layer4 checkpoint after-agent
layer4 seal --claims artifact_existed tests_passed no_secrets
layer4 score --metric lci
layer4 export --format receipt report
layer4 verify receipt.l4receipt
```

## Receipt Report Summary

A V1 human-readable report should show:

```text
Layer4Meter V1 Receipt

Project: AgentLedger
Session Window: start → end
Mode: agent workload / idle baseline / human baseline
Files Changed: N
Git Delta: N staged, N modified, commit hash if present
Commands Recorded: N
Tests: passed / failed / not run
Artifact: exists / missing
Raw LCI: number
Adjusted LCI: number if baselines exist
Proof Density: verified claims / total claims
VerifiedArtifactValue: value or unverified
ValuePerLCI: value or unverified
Merkle Root: sha256:...
```

## Proof Density

```text
ProofDensity = verified_claims / total_claims
```

Claim examples:

```text
artifact_existed
tests_passed
source_hash_bound
receipt_exported
no_secrets_detected
build_completed
```

Claims must be evidence-backed.

If evidence is missing:

```text
claim_status = unverified
```

## Product Positioning

Short:

> Layer4Meter is substrate accounting for AI-native Mac work.

Investor/product explanation:

> Layer4Meter turns local AI work from “I made a thing” into “here is the signed receipt showing what machine work produced it, what proofs validate it, and whether the output was worth the substrate cost.”

Buyer explanation:

> Prove what your AI agents produced, what it cost, and whether it was worth it.

## Integration With OverLanguage

```text
Intent → Agent Work → Artifact → Layer4Meter Receipt → Lambda Score → Buyer Packet
```

Layer4Meter supplies the denominator for OverLanguage value claims.

```text
τ = receipt strength / (1 + λ)
ValuePerLCI = VerifiedArtifactValue / LCI_adjusted
```

## Final Law

```text
No denominator, fake economics.
Receipt plus denominator, production accounting.
```

Layer4Meter becomes serious when every artifact can answer:

1. What changed?
2. What commands ran?
3. What files were created?
4. What tests passed?
5. What substrate cost was measured?
6. What proof exists?
7. What value claim is allowed?
