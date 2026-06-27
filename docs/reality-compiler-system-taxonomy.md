# Reality Compiler: System Taxonomy for Transferable Artifact Production

## Status

This document defines the umbrella naming hierarchy for the stack previously described as OverLanguage / OverProgramming / Layer4Meter / Glyph ML / ReceiptOS.

The mature umbrella name is:

> **Reality Compiler**

The reason is simple: OverLanguage sounds like a language. The full system is bigger than a language.

Reality Compiler compiles local work into verified transferable value.

## Master Statement

```text
Reality Compiler turns local work into verified transferable value.
```

Expanded:

```text
intent → glyph → workflow → agents → files → substrate work → proof → receipt → transferable value
```

Output:

```text
verified artifact + receipt + lambda score + buyer packet
```

## Naming Hierarchy

```text
Reality Compiler
  writes in OverLanguage 2.0
  using Glyph Notation
  executes through Agent Runtime
  measures through Layer4Meter
  records through ReceiptOS
  scores through LambdaBase
  exports LambdaReceipts
```

## Taxonomy

```text
Glyphs          = symbolic compression layer
OverLanguage    = grammar layer
OverProgramming = execution philosophy
Reality Compiler = product / system layer
ReceiptOS       = ledger / proof layer
LambdaBase      = transferability / value database
GlyphVM         = symbolic runtime
Layer4Meter     = substrate accounting layer
JORKI           = file-access substrate
GlyphLock       = time-gated codec/access layer
```

## Stack

```text
Reality Compiler
├── Glyph Notation
├── OverLanguage Grammar
├── Agent Runtime
├── JORKI File Gateway
├── GlyphLock Enigma Envelope
├── Layer4Meter Substrate Meter
├── ReceiptOS / zkReceipt Ledger
├── Lambda Transferability Scorer
├── LambdaBase Value Database
└── Financeable Artifact Exporter
```

## Product Boundary

Reality Compiler is not an AR/spatial design tool.

Apple already uses the Reality naming space for spatial tooling such as Reality Composer Pro, which Apple describes as a tool for rapidly iterating, previewing, and preparing 3D content for visionOS, iOS, and more.

Therefore the positioning must be explicit:

```text
Reality Compiler is not for composing 3D scenes.
Reality Compiler compiles intent, work, proof, and substrate cost into transferable artifact value.
```

## Standards Alignment

Reality Compiler should not invent a private proof universe when existing provenance and credential models already exist.

Relevant standards alignment:

- **SLSA provenance**: software provenance describes where, when, and how artifacts were produced so consumers can verify they were built according to expectations and optionally rebuild them.
- **W3C PROV**: provenance is information about entities, activities, and people involved in producing a data item or thing, useful for assessing quality, reliability, or trustworthiness.
- **W3C Verifiable Credentials**: a verifiable credential is a tamper-evident credential whose authorship can be cryptographically verified.

Reality Compiler should export its receipts in a way that can later map into these provenance and credential models.

## Core Compilation Pipeline

```text
Intent
→ Glyph Notation
→ OverLanguage workflow
→ Agent Runtime execution
→ JORKI file access
→ GlyphLock access envelope when needed
→ Layer4Meter substrate accounting
→ ReceiptOS proof ledger
→ LambdaBase transferability score
→ Buyer packet
```

## Glyph Form

```text
Intent → ⧉◇@L → H@L Æ R Æ λ⁻¹ = ◎ → $
```

Interpretation:

```text
Intent becomes compressed symbolic workflow.
Workflow produces hash-bound artifact.
Artifact binds to receipt.
Receipt yields inverse-lambda transferability score.
Verified artifact becomes buyer-transferable value.
```

## Component Definitions

### Glyph Notation

The symbolic compression alphabet.

Purpose:

- compress repetitive workflow structures
- encode operators directly
- support machine-readable traces
- reduce verbose prompt/log overhead

### OverLanguage 2.0

The grammar layer.

Purpose:

- describe workflows
- bind intent to steps
- declare artifacts
- define proof claims
- express receipt policies

### OverProgramming

The execution philosophy.

Purpose:

- treat programming as artifact production plus proof
- coordinate agents, tools, files, and receipts
- keep user intent above individual apps

### Agent Runtime

The execution layer.

Purpose:

- run coding/research/build/test agents
- coordinate local and remote tools
- emit command receipts
- report failures and retries

### JORKI

The file-access substrate.

Purpose:

- turn large files into queryable state
- expose metadata/search/chunk/SQL/MCP surfaces
- avoid unnecessary full-file transfer

### GlyphLock

The time-gated codec/access envelope.

Purpose:

- make files economically visible before decode
- make full consumption conditional on dictionary/key/time authorization
- support preview, unlock, query, revoke

### Layer4Meter

The substrate accounting layer.

Purpose:

- record project file deltas
- record Git diffs
- record command/build/test events
- sample resource usage
- produce LCI and proof density
- bind substrate work to artifacts

### ReceiptOS

The ledger/proof layer.

Purpose:

- collect receipts
- hash shards
- compute Merkle roots
- sign or notarize receipts when supported
- export verifier packets

### LambdaBase

The transferability/value database.

Purpose:

- store lambda scores
- store artifact readiness
- track value evidence
- distinguish verified value from assumed value
- support buyer packets

### LambdaReceipt

The output artifact.

Purpose:

- bundle verified artifact metadata
- receipt chain
- proof density
- LCI denominator
- lambda transferability score
- buyer-facing summary

## Output Object

```text
.lambda_receipt
├── artifact_manifest.json
├── provenance.json
├── layer4_receipt.l4receipt
├── glyph_trace.glyph
├── over_workflow.over
├── claims.jsonl
├── value_evidence.json
├── lambda_score.json
├── merkle_root.txt
└── buyer_packet.md
```

## Product Names

Use this hierarchy:

```text
Umbrella:       Reality Compiler
Syntax:         OverLanguage 2.0
Alphabet:       Glyph Notation
Runtime:        GlyphVM / Agent Runtime
Receipt layer:  ReceiptOS
Meter:          Layer4Meter
Value DB:       LambdaBase
Output:         LambdaReceipt
```

Avoid making one name carry everything.

## Positioning Options

### If emphasizing notation

```text
OverLanguage 2.0
```

### If emphasizing product/system

```text
Reality Compiler
```

### If emphasizing proof

```text
ReceiptOS
```

### If emphasizing value transferability

```text
LambdaBase
```

### If emphasizing runtime

```text
GlyphVM
```

## Recommended External Line

```text
Reality Compiler converts AI-native work into verified, transferable artifact value.
```

## Recommended Technical Line

```text
Reality Compiler compiles intent, agent execution, file changes, substrate cost, proof claims, and value evidence into LambdaReceipts.
```

## Recommended Buyer Line

```text
Show me what was built, what proof exists, what it cost, and why it is transferable.
```

## Boundary Conditions

Reality Compiler should avoid overclaiming.

- It does not compile physical reality.
- It compiles workflows, artifacts, receipts, proofs, and value evidence.
- It does not create verified value from nothing.
- Value must be backed by evidence.
- Substrate cost is measured or estimated, not magically discovered.
- ZK should only be claimed when an actual proof and verifier exist.
- Receipts should eventually map to provenance/credential standards rather than remaining private lore.

## Final Law

```text
OverLanguage writes the workflow.
Layer4Meter measures the denominator.
ReceiptOS proves the artifact.
LambdaBase scores transferability.
Reality Compiler packages the whole thing into value.
```
