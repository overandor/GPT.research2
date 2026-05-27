# BitNet Provenance Runtime

BitNet is a local-first cryptographic filesystem provenance engine.

Its public tagline is:

```text
Self-proving folders.
```

Its core primitive is:

```text
folder -> SHA-256 file hashes -> Merkle root -> receipt -> watcher -> optional notarization
```

BitNet continuously hashes folders into Merkle trees so a user can cryptographically verify what files existed at a specific moment in time.

This document explains the real problems BitNet targets, the mathematical model behind the system, the guarantees it can provide, and the limits it must honestly acknowledge.

---

## 1. The real-world problem

Modern software and data work has a provenance gap.

Developers, researchers, companies, auditors, and AI-assisted builders increasingly need to answer questions like:

```text
What exactly was in this folder yesterday?
Did any file change silently?
Did this dataset mutate after the experiment?
Did this AI-generated code artifact remain intact?
Which build artifacts correspond to this source tree?
Can I prove this folder state existed before a dispute, release, audit, or incident?
```

Existing systems only partially solve this.

Git tracks committed source code, but not arbitrary folders, generated artifacts, datasets, local outputs, temporary build trees, model files, design files, or private working directories.

Cloud sync stores versions, but its integrity model is controlled by the cloud provider and does not usually produce compact, portable, cryptographic proof receipts.

Checksums prove one file, but not an entire folder state with many files and paths.

Backups preserve data, but they do not necessarily give a minimal proof that a precise directory state existed at a precise time.

Blockchains can timestamp small data, but they are inefficient for storing whole folders and should not receive private file contents.

BitNet fills this gap by turning a folder into a deterministic cryptographic state object.

---

## 2. The core idea

A folder is treated as an ordered set of file claims.

Each file claim contains at minimum:

```text
relative_path
file_size
content_hash
metadata_hash, optional
```

The content hash is computed locally:

```text
h_i = SHA256(file_bytes_i)
```

The folder state is then reduced into a Merkle root:

```text
R = MerkleRoot(h_1, h_2, ..., h_n)
```

The root `R` is a compact commitment to the entire folder contents.

If one byte in one file changes, the corresponding leaf hash changes. If one leaf hash changes, the Merkle root changes with overwhelming probability.

That means BitNet can compress an entire folder state into one cryptographic fingerprint.

---

## 3. Mathematical model

Let a folder snapshot be represented as a finite set:

```text
F = { f_1, f_2, ..., f_n }
```

Each file `f_i` has:

```text
p_i = normalized relative path
b_i = file byte content
s_i = file size
```

Define a leaf commitment:

```text
L_i = H(p_i || s_i || H(b_i))
```

where:

```text
H = SHA-256
|| = byte concatenation with canonical separators
```

Sort all leaves deterministically by normalized path:

```text
L_sorted = sort_by_path(L_1, ..., L_n)
```

Build the Merkle tree recursively:

```text
M_0 = L_sorted
M_{k+1}[j] = H(M_k[2j] || M_k[2j+1])
```

If a level has an odd number of nodes, BitNet must use one canonical rule, such as duplicating the final node or promoting it unchanged. The rule must be documented and tested.

The final root is:

```text
R(F) = M_t[0]
```

where `M_t` has one element.

This root is the folder commitment.

---

## 4. Collision resistance claim

BitNet relies on the collision resistance of SHA-256.

Informally:

It should be computationally infeasible to find two different inputs `x` and `y` such that:

```text
SHA256(x) = SHA256(y)
```

Therefore it should be computationally infeasible to construct two different folder states `F` and `F'` such that:

```text
R(F) = R(F')
```

unless the attacker can find a SHA-256 collision or exploit a canonicalization bug.

This gives BitNet its central integrity guarantee:

```text
If two verified folder roots match, then the corresponding canonical folder states are equal with cryptographic confidence.
```

More precisely:

```text
R(F) = R(F') => F = F'
```

except with negligible probability under SHA-256 collision assumptions and correct canonical serialization.

---

## 5. Tamper detection proof sketch

Suppose an attacker modifies one byte in file `f_k`.

Original file bytes:

```text
b_k
```

Tampered file bytes:

```text
b'_k
```

If:

```text
b_k != b'_k
```

then with overwhelming probability:

```text
SHA256(b_k) != SHA256(b'_k)
```

Therefore:

```text
L_k != L'_k
```

Because a Merkle parent is computed by hashing child nodes, every parent along the path from `L_k` to the root changes:

```text
P_k != P'_k
...
R(F) != R(F')
```

So the folder root changes.

Therefore BitNet detects the tampering by comparing the newly computed root to the previous receipt root.

This solves silent file tampering for any folder that is periodically or continuously scanned.

---

## 6. Inclusion proof

A Merkle proof lets BitNet prove that one file was included in a folder snapshot without publishing the entire folder.

For a target leaf `L_i`, the proof contains the sibling hashes on the path from `L_i` to the root:

```text
proof_i = [sibling_0, sibling_1, ..., sibling_k]
```

Verification recomputes:

```text
current = L_i
current = H(current || sibling_0) or H(sibling_0 || current)
...
current = R
```

If the recomputed value equals the receipt root, then `f_i` was included in the committed folder state.

This gives BitNet a compact proof system:

```text
Proof size = O(log n)
Verification time = O(log n)
Root size = O(1)
```

For a folder with one million files, the root is still one hash, and an inclusion proof only needs about 20 sibling hashes.

---

## 7. Why this solves real problems

### 7.1 Software supply-chain integrity

A release can include a BitNet receipt proving exactly which source files, generated files, and build artifacts existed at release time.

Problem solved:

```text
Did this release come from this exact folder state?
```

BitNet answer:

```text
Recompute the folder root and compare it to the signed receipt root.
```

### 7.2 AI-generated code provenance

AI-generated code often enters repositories through copy-paste, IDE assistants, chat exports, generated patches, or autonomous agents.

Problem solved:

```text
Can I prove what AI-generated artifact existed before later human edits?
```

BitNet answer:

```text
Commit a receipt before and after edits. The difference between roots proves the artifact changed.
```

### 7.3 Dataset integrity

Research datasets and model training sets can mutate accidentally or maliciously.

Problem solved:

```text
Was this model trained on the same dataset claimed in the paper or audit?
```

BitNet answer:

```text
Publish a dataset root. Anyone with the dataset can recompute and verify it.
```

### 7.4 Build artifact verification

Build outputs are often trusted implicitly.

Problem solved:

```text
Do these binaries correspond to the audited build folder?
```

BitNet answer:

```text
Hash the build output directory and attach the root to the release receipt.
```

### 7.5 Legal and compliance evidence

Audits often require evidence that certain files existed at a certain time.

Problem solved:

```text
Can I prove this evidence package was not modified after collection?
```

BitNet answer:

```text
Produce a timestamped receipt and optionally notarize only the root hash.
```

### 7.6 Incident response

After a breach, teams need to know when malicious files appeared or which files changed.

Problem solved:

```text
Which snapshot first introduced the suspicious file?
```

BitNet answer:

```text
Compare receipt timeline roots and file-level leaf records.
```

---

## 8. Receipt model

A BitNet receipt should be a canonical JSON object:

```json
{
  "schema_version": "bitnet/0.1",
  "type": "FolderSnapshotReceipt",
  "root_path_hash": "sha256:...",
  "merkle_root": "sha256:...",
  "file_count": 1234,
  "total_bytes": 987654321,
  "created_at": "2026-05-27T00:00:00Z",
  "previous_receipt_hash": "sha256:...",
  "hash_algorithm": "SHA-256",
  "canonicalization": "bitnet-path-v1",
  "signature": "optional-signature",
  "anchor": {
    "type": "optional-solana-memo",
    "tx": "optional"
  }
}
```

The receipt hash is:

```text
receipt_hash = SHA256(canonical_json(receipt_without_signature))
```

If receipts are chained:

```text
receipt_t.previous_receipt_hash = receipt_hash_{t-1}
```

then BitNet creates an append-only local evidence chain.

This resembles a local transparency log.

---

## 9. Receipt chain proof

Let each receipt contain the previous receipt hash:

```text
C_t = H(R_t || C_{t-1} || metadata_t)
```

where:

```text
R_t = folder Merkle root at time t
C_t = receipt chain hash at time t
```

If an attacker modifies an old receipt `C_k`, then every later chain hash changes:

```text
C_k != C'_k
C_{k+1} != C'_{k+1}
...
C_t != C'_t
```

Therefore tampering with historical evidence becomes detectable.

If the latest chain hash has been signed or externally notarized, then the attacker cannot rewrite history without breaking the signature or notarization.

---

## 10. Optional blockchain notarization

BitNet does not need a blockchain to work.

The local guarantees come from hashing, Merkle proofs, receipt canonicalization, and signatures.

A blockchain can add public timestamping.

The correct blockchain use is:

```text
store only the Merkle root or receipt hash
```

Never store private file contents.

Optional Solana memo anchoring can prove:

```text
This root hash existed no later than block/time T.
```

It does not prove the semantic quality of the files.
It does not prove authorship by itself.
It does not prove legal ownership by itself.
It only proves public timestamped existence of a cryptographic commitment.

That is still valuable.

---

## 11. What BitNet does not claim

BitNet must be honest.

It does not prove that files are good.

It does not prove that code is secure.

It does not prove that a person authored a file unless signatures or identity evidence are attached.

It does not prevent tampering before the first snapshot.

It does not protect files from deletion unless snapshots and receipts are backed up.

It does not replace Git.

It does not replace backups.

It does not replace SLSA, Sigstore, SBOMs, or CI security.

It complements them by creating a compact, local, cryptographic folder-state primitive.

---

## 12. Why the primitive is powerful

BitNet converts an arbitrary mutable folder into a verifiable mathematical object.

Before BitNet:

```text
folder = loose collection of files
```

After BitNet:

```text
folder = cryptographic commitment + receipt history + verifiable proofs
```

This is powerful because many systems can compose with a Merkle root:

- GitHub Actions can attach it to releases.
- CI can verify it before deployment.
- Auditors can validate evidence packages.
- Researchers can publish dataset roots.
- AI systems can issue provenance receipts for generated artifacts.
- Solana or another timestamping layer can notarize root existence.
- Sigstore can sign receipts.
- IPFS can store receipt bundles.

The root becomes a universal reference to folder state.

---

## 13. Formal guarantee summary

Assuming:

1. SHA-256 collision resistance.
2. Deterministic file traversal.
3. Canonical path normalization.
4. Canonical JSON receipt serialization.
5. Correct implementation.
6. Secure storage or external notarization of receipt hashes.

BitNet provides:

### Integrity

```text
Any change to committed file contents changes the folder root with overwhelming probability.
```

### Inclusion

```text
A Merkle proof can prove a file was included in a folder snapshot in O(log n) space and time.
```

### Non-equivocation, if receipt chains are used

```text
Historical receipt tampering changes all later receipt-chain hashes.
```

### Public existence, if notarized

```text
An externally anchored root proves the receipt existed no later than the anchor timestamp.
```

### Portability

```text
A receipt can be verified independently of the original BitNet process if the canonical rules are known.
```

---

## 14. Practical examples

### Example: one-file tamper

Original:

```text
config.json = {"debug": false}
```

Hash:

```text
h1 = SHA256(config.json)
```

Tampered:

```text
config.json = {"debug": true}
```

Hash:

```text
h1' = SHA256(config.json')
```

Since file bytes changed:

```text
h1 != h1'
```

Therefore:

```text
MerkleRoot(F) != MerkleRoot(F')
```

BitNet detects the tamper.

### Example: dataset publication

A researcher publishes:

```text
training_dataset_root = sha256:abc123...
```

Another lab downloads the dataset and runs BitNet.

If the computed root matches, the dataset is equivalent under BitNet canonicalization.

If it does not match, the dataset changed.

### Example: AI code artifact

An AI agent generates a folder.

BitNet snapshots it:

```text
R_0 = MerkleRoot(agent_output_folder)
```

A developer edits it.

BitNet snapshots again:

```text
R_1 = MerkleRoot(edited_folder)
```

If:

```text
R_0 != R_1
```

then the post-edit folder is provably different from the original generated artifact.

This creates a clean boundary between generated output and later human modification.

---

## 15. Why this is not just Git

Git is excellent for source control, but BitNet targets a different layer.

Git requires intentional staging and committing.

BitNet can watch arbitrary folders continuously.

Git is repository-oriented.

BitNet is folder-state-oriented.

Git stores history.

BitNet emits portable receipts and Merkle proofs.

Git can track text and binary files, but it is not usually used for generated artifacts, datasets, local evidence folders, model outputs, or compliance bundles.

BitNet can cover those folders without changing their workflow.

The best framing is:

```text
Git tracks development history.
BitNet proves filesystem state.
```

They are complementary.

---

## 16. Why this is not just IPFS

IPFS gives content addressing.

BitNet gives local continuous provenance over folder state.

IPFS answers:

```text
What content corresponds to this CID?
```

BitNet answers:

```text
What was in this local folder at this time, and has it changed since?
```

BitNet can optionally export receipts or snapshots to IPFS later, but IPFS is not required for the core guarantee.

---

## 17. Why this is not just a checksum

A checksum usually proves one blob.

A BitNet root proves a structured set of files.

A checksum has no efficient per-file inclusion proof.

A Merkle tree does.

A checksum does not naturally support partial verification.

A Merkle tree does.

A checksum does not create a timeline.

BitNet receipts can.

---

## 18. The real primitive

The primitive is not the dashboard.

The primitive is not Solana anchoring.

The primitive is not a valuation layer.

The primitive is:

```text
canonical folder state -> cryptographic commitment -> portable receipt -> verifiable change history
```

That is the core.

Everything else is interface.

---

## 19. Strategic launch rule

BitNet should remain small and sharp.

Do not describe it as a token protocol.

Do not describe it as a DeFi primitive.

Do not describe it as collateral infrastructure.

Do not describe it as governance.

Describe it as:

```text
local-first cryptographic provenance for folders
```

That is enough.

---

## 20. Short public explanation

BitNet makes folders self-proving.

It scans every file locally, hashes the contents, builds a Merkle tree, and emits a receipt containing the folder root. Later, anyone can rescan the folder and verify whether the contents are exactly the same. A single changed byte changes the root. A Merkle proof can prove a specific file existed in the snapshot without publishing the whole folder. Optional notarization can timestamp the root publicly without exposing private files.

This solves a real and growing problem: in an AI-generated, supply-chain-sensitive, compliance-heavy software world, people need a simple way to prove what files existed, when they existed, and whether they changed.

BitNet is that primitive.
