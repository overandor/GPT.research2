# OverLanguage 2.0 + GlyphForge + Layer4Meter Specification

## Summary

This specification defines **OverLanguage 2.0**, a glyph-native meta-language for programming AI-native production systems rather than only software functions.

Traditional programming compiles instructions into code behavior.

OverProgramming compiles intent into:

- agent tasks
- files
- workflows
- runtime capture
- receipts
- proofs
- transferability scores
- buyer-ready artifacts
- economic value packets

The root law is:

```text
Program = instructions for machines.
OverProgram = instructions for production reality.
```

The master glyph is:

```text
⧉◇@L → H@L Æ R Æ λ⁻¹ = ◎ → $
```

Meaning:

A stationary artifact at location becomes hash-anchored, receipt-bound, transferable, verified, and financeable.

---

## Core Pipeline

```text
Intent
→ Contract
→ Agent execution
→ Runtime capture
→ Artifact creation
→ Receipt binding
→ Lambda scoring
→ Buyer packaging
→ Revenue attempt
```

The compiler should implement these passes:

1. Parse intent.
2. Expand glyphs.
3. Build contract.
4. Assign agents.
5. Generate files.
6. Execute workflow.
7. Capture substrate.
8. Hash artifacts.
9. Generate receipt.
10. Score lambda.
11. Verify state.
12. Package for sale.
13. Feed result back into memory.

---

## OverLanguage 2.0 Layers

### Layer 0: Glyph Layer

The compressed symbolic substrate.

```text
□      file
◇      artifact
⧉      stationary object
H      hash
L      location
R      receipt
λ      friction
λ⁻¹    transferability force
χ      hidden compute
Σ      shard set
M      Merkle root
ZK     proof
◎      verified
$      financeable
Æ      bind
→      emit / derive
⟲      recursive loop
```

### Layer 1: Intent Layer

Captures the human-level objective.

Example:

```text
Intent:
  Build a Mac app that records AI agent activity and produces receipts.
```

OverLanguage asks:

- What artifact should exist?
- What proof should exist?
- What machine events matter?
- What should be sellable?
- What counts as completion?

### Layer 2: Contract Layer

Turns vague intent into enforceable requirements.

```text
Requires:
  repo
  macOS target
  recorder permissions
  export format
  verification rules

Ensures:
  app exists
  receipt exports
  file hashes match
  no secrets detected
  transferability score produced
```

### Layer 3: Agent Layer

Assigns production roles.

```text
CHATGPT    → architecture / spec / critique
WINDSURF   → code edits / repo operations
CODEX      → patch generation / tests
CLAUDE     → deep refactor / reasoning
XCODE      → native build / signing / diagnostics
TERMINAL   → commands / receipts / verification
```

### Layer 4: Runtime/Substrate Layer

Captures invisible compute.

```text
χCPU + χIO + χMEM + χIDX + χNET → LCI
```

Meaning:

CPU, disk, memory pressure, indexing, network activity, daemons, snapshots, retries, and background substrate activity become a **Latent Compute Index**.

### Layer 5: Receipt Layer

Every output receives proof.

```text
◇ → H
H Æ R
R Æ σ
R = ◎
```

### Layer 6: Transfer Layer

Scores transferability through lambda.

```text
τ = R / (1 + λ)
```

Where:

- high λ = local paths, hidden keys, broken dependencies, missing docs, missing tests
- low λ = clean install, receipts, tests, docs, hashes, portable build

### Layer 7: Economic Layer

Asks:

- Who buys this?
- What proof do they need?
- What packet closes the sale?
- What is the price?
- What artifact is missing?

---

## Canonical OverLanguage Example

```text
overprogram AgentLedger {
  intent:
    "Build a Mac-native black box recorder for AI work."

  object:
    ◇ = "Agent Activity Ledger"

  anchor:
    ⧉◇@L

  capture:
    screen
    files
    git
    terminal
    build
    substrate

  prove:
    H@L Æ R
    R Æ σ
    R ⊢ tests_passed
    R ⊢ no_secrets_detected
    R ⊢ artifact_existed

  score:
    λ = local_paths + secrets + runtime_drift + docs_gap + test_gap
    τ = R / (1 + λ)

  output:
    app
    receipt.pdf
    receipt.zip
    verifier.cli
    buyer_packet.pdf

  success:
    ◎ and τ > 80 and buyer_packet exists

  economic:
    price = "$10k pilot"
    buyer = "AI agencies, CTOs, Mac dev teams"
}
```

---

## GlyphForge

GlyphForge is the recursive glyph engine.

```text
Seed → Grammar → Mutation → Receipt → Score → Archive → New Seed
```

A glyph is not decorative. It must contain:

- meaning
- expansion
- proof role
- machine payload
- transferability score
- relationship to parent glyphs
- receipt hash

Recursive loop:

```text
G₀ = seed glyph
Gₙ₊₁ = mutate(bind(split(score(Gₙ))))
```

Example evolution:

```text
□@L
□@L → H@L
H@L Æ R
H@L Æ R Æ λ⁻¹
H@L Æ R Æ λ⁻¹ = ◎
◇ = H@L Æ R Æ λ⁻¹ = ◎ → $
```

---

## Glyph Scoring

```text
GlyphScore =
  compression
+ meaning density
+ machine executability
+ proof strength
+ transferability
+ novelty
+ commercial usefulness
- ambiguity
- decorative noise
```

A valid glyph must expand into machine-checkable meaning.

Invalid:

```text
✦⟁☍⌁
```

Valid:

```text
H@L Æ R Æ λ⁻¹ = ◎
```

Because it expands into:

- hash at location
- bound to receipt
- low friction
- verified

---

## Glyph Receipt Record

Each glyph should be stored as a ledger entry:

```json
{
  "glyph": "H@L Æ R Æ λ⁻¹ = ◎",
  "plain_english": "A stationary file is verified by hash-at-location, receipt binding, and low transfer friction.",
  "role": "zero_copy_transferability",
  "parents": ["□@L", "H Æ R", "λ⁻¹"],
  "hash": "sha256:...",
  "score": 91,
  "created_at": "timestamp",
  "machine_payload": {
    "object": "file",
    "anchor": "location",
    "proof": "receipt",
    "metric": "inverse_lambda",
    "state": "verified"
  }
}
```

---

## Layer4Meter

Layer4Meter captures hidden substrate compute.

The system should measure five planes:

1. Visual plane  
   Screen checkpoints, active windows, UI state, visible artifacts.

2. File plane  
   File deltas, hashes, build artifacts, cache growth.

3. Process plane  
   Process spawns, terminal commands, app execution events.

4. Power/performance plane  
   CPU time, disk writes, memory pressure, network bytes, thermal behavior.

5. Time/snapshot plane  
   Before/after state, APFS or Time Machine-style anchors, artifact existence proof.

---

## Latent Compute Index

Initial metric:

```text
LCI =
  α·CPU_seconds
+ β·GPU_or_media_activity
+ γ·disk_write_MB
+ δ·file_event_count
+ ε·process_spawn_count
+ ζ·network_bytes
+ η·memory_pressure_score
+ θ·snapshot_delta_MB
+ ι·screen_state_changes
+ κ·agent_idle_or_retry_time
```

Compute hidden lift:

```text
Hidden Compute Lift =
Agent Workload LCI - Human Baseline LCI - Idle Baseline LCI
```

Derived metrics:

```text
Cost per artifact = energy + time + API spend + disk growth + retry waste
Proof density = verified events / total events
Agent efficiency = useful output / latent compute lift
Waste ratio = retries + failed builds + dead loops / total substrate activity
Revenue readiness = artifact value / hidden compute cost
```

---

## Receipt Format

```text
.l4receipt
├── manifest.json
├── events.sqlite
├── shards/
│   ├── visual.jsonl
│   ├── files.jsonl
│   ├── process.jsonl
│   ├── power.jsonl
│   ├── git.jsonl
│   └── snapshots.jsonl
├── hashes/
│   ├── merkle_root.txt
│   └── shard_hashes.json
├── proofs/
│   ├── no_secrets.proof
│   ├── tests_passed.proof
│   └── artifact_existed.proof
└── report.pdf
```

---

## Proposed Repository Structure

```text
overlanguage/
  grammar/
    glyphs.yaml
    operators.yaml
    schemas.yaml

  core/
    parser.py
    compiler.py
    runtime.py
    receipts.py
    lambda_score.py
    verifier.py
    glyphforge.py
    layer4meter.py

  adapters/
    git_adapter.py
    file_adapter.py
    mac_adapter.py
    windsurf_adapter.py
    terminal_adapter.py

  examples/
    agent_ledger.over
    dmg_packager.over
    revenue_lab.over

  tests/
    test_parser.py
    test_receipts.py
    test_lambda_score.py
    test_glyphforge.py
    test_layer4meter.py
```

---

## MVP Command

```text
over run examples/agent_ledger.over
```

Expected output:

```text
Generated:
  build_plan.md
  artifact_manifest.json
  receipt.json
  lambda_score.json
  buyer_packet.md
```

---

## Product Claim

OverLanguage does not compile only to code.

It compiles to:

- code
- workflow
- proof
- artifact
- transferability
- buyer packet
- economic value

Root law:

```text
artifact → receipt → score → mutation → better artifact
```

Glyph form:

```text
◇ → R → τ → Δ◇ ⟲
```

Meaning:

Artifact produces receipt, receipt produces transferability score, score causes artifact improvement, and the loop repeats.

---

## Acceptance Criteria

The MVP is complete when:

- `.over` files can be parsed.
- At least one glyph expands into a machine-readable contract.
- A sample artifact manifest is generated.
- A receipt JSON is generated.
- A lambda score is computed.
- A buyer packet Markdown file is generated.
- GlyphForge can mutate at least one seed glyph into valid descendants.
- Layer4Meter can produce a mock or real LCI receipt.
- Tests pass for parser, receipt generation, lambda scoring, and glyph validation.

---

## First Implementation Target

Build the smallest working interpreter.

Do not start with full macOS capture, full ZK, or real economic settlement.

Start with:

1. Parser.
2. Glyph dictionary.
3. Contract compiler.
4. Manifest generator.
5. Receipt generator.
6. Lambda scorer.
7. Buyer packet exporter.
8. GlyphForge mutation loop.
9. Mock Layer4Meter receipt.

---

## Related Research Thread

This document is the implementation-facing companion to the broader research direction around Antonymified File Receipts and BlurHash64. That research direction frames controlled disclosure as a way to make digital artifacts priceable without direct consumption: LLMs create non-consumable surrogates, while hashes, receipts, leakage tests, oracles, bonds, and settlement records supply accountability.

In this repository, OverLanguage 2.0 is the production-runtime layer. Antonymified File Receipts and BlurHash64 are the disclosure and market layers that can sit above or beside it.
