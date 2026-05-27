# BitNet Provenance Runtime

BitNet is a local-first cryptographic filesystem provenance engine.

Core primitive:

folder -> SHA-256 file hashes -> Merkle root -> receipt -> watcher -> optional notarization

Tagline:

Self-proving folders.

BitNet continuously hashes folders into Merkle trees so you can cryptographically verify what files existed at any moment in time.
