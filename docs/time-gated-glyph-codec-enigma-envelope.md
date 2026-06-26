# Time-Gated Glyph Codec / JORKI Enigma Envelope

## Status

This document defines a new primitive that sits between BlurHash64, Antonymified File Receipts, JORKI, and OverLanguage.

The primitive is not “compression by secrecy.” It is:

```text
compression with private side information + cryptographic protection + time-gated decoder access
```

Product names:

- **Time-Gated Glyph Codec**
- **GlyphLock Compression**
- **JORKI Enigma Envelope**
- **Antonymified Enigma Receipt**
- **Glyph Enigma Envelope**, abbreviated `GE²`

## Core Thesis

A file can be transformed into a partially interpretable glyph packet that is safe to price, route, verify, or preview, while full reconstruction requires a decoder dictionary, cryptographic key, issuer policy, and time-valid authorization.

Strong line:

> We are not hiding the file. We are splitting its meaning across a visible glyph packet and a time-gated decoder.

Sharper line:

> The file becomes a puzzle whose solution is not intelligence, but authorization.

## Pipeline

```text
File
→ semantic segmentation
→ glyph/operator dictionary encoding
→ lossless compression
→ encrypted envelope
→ public blurred receipt
→ time-gated decoder
→ full unfold / query access
```

Formal primitive:

```text
G = Encode(File, Dictionary, TimeKey, Policy)
File = Decode(G, Dictionary, TimeKey, Policy)
```

Where:

```text
G  = glyph packet
D  = decoder dictionary / rulebook
Kt = time-derived key or time-authorized unlock
P  = issuer policy
R  = receipt
```

Access law:

```text
G alone             → priceable blur
G + D               → interpretable structure
G + D + Kt          → reconstructable/queryable file
G + D + Kt + R      → accountable access
```

## Security Boundary

The codec layer and the security layer must not be confused.

```text
Codec ≠ Security
Compression ≠ Encryption
Obscurification ≠ Proof
TOTP ≠ File Key
```

The glyph/dictionary layer creates controlled interpretability and possible compression. Cryptography protects confidentiality and integrity. The time gate authorizes access to key material or decoder capability.

Do not rely on a secret algorithm alone. Assume the attacker can learn the algorithm. The protected material must be the key, dictionary seed, recipient capability, session policy, and time-gated unlock.

## Compression Model

Obscurification alone does not compress. It only hides, rearranges, or reduces interpretability.

Compression happens because the issuer and authorized decoder share side information:

- dictionary
- rulebook
- symbol table
- placement grammar
- session seed
- repeated structure model
- semantic segment map

The visible packet does not need to carry all meaning if the decoder dictionary carries part of the missing structure.

The disciplined phrasing is:

> side-information compression with gated decoding

## Two-Layer Disclosure

### Outer Layer: Minor Interpretability

The buyer, LLM, or verifier can see:

- file class
- shape
- capability hints
- schema hints
- chunk map
- Merkle root
- proof hooks
- expiry
- safe preview
- query rights
- issuer identity
- revocation rule

But cannot consume or reconstruct the source.

### Inner Layer: Full Unfold

Authorized user receives:

- decoder dictionary
- wrapped payload key
- time-valid authorization
- query rights
- optional raw body access
- full semantic index
- receipt verification

## Envelope Object

```text
GE² = Glyph Enigma Envelope
```

```json
{
  "kind": "ge2.envelope.v1",
  "public_preview": {
    "mode": "antonymified_blur",
    "file_class": "source|pdf|image|dataset|archive|model|unknown",
    "capabilities": ["meta", "summary", "search", "chunk", "sql"],
    "safe_description": "non-consumable preview"
  },
  "glyph_payload": {
    "encoding": "glyphlock.v1",
    "packet_hash": "sha256:...",
    "compressed_size": 0,
    "operator_ratio": 0.40
  },
  "dictionary": {
    "dictionary_id": "sha256:...",
    "dictionary_version": "v1",
    "dictionary_policy": "encrypted_or_remote_gated"
  },
  "identity": {
    "source_merkle_root": "sha256:...",
    "packet_merkle_root": "sha256:..."
  },
  "crypto": {
    "aead": "AES-256-GCM or equivalent AEAD",
    "aad": "public receipt fields",
    "iv_policy": "unique per key and invocation",
    "wrapped_key_policy": "recipient + time gate"
  },
  "time_gate": {
    "mode": "totp_or_signed_time_window",
    "window_seconds": 30,
    "not_before": "timestamp_or_null",
    "not_after": "timestamp_or_null"
  },
  "query_policy": {
    "pre_decode": ["meta", "capabilities", "safe_preview"],
    "post_decode": ["summary", "search", "chunk", "sql"],
    "raw_body_allowed": false
  },
  "receipt": {
    "issuer": "did_or_account",
    "issued_at": "timestamp",
    "policy_hash": "sha256:...",
    "receipt_hash": "sha256:..."
  }
}
```

## Key Schedule

Payload encryption should use a high-entropy random file key.

```text
payload_key = random 256-bit key
compressed_payload = glyph_codec(file, dictionary)
ciphertext = AEAD_encrypt(payload_key, compressed_payload, public_receipt_as_AAD)
```

Unlock requires:

```text
recipient identity
+ issuer policy
+ valid time window / TOTP / signed challenge
+ wrapped payload key
+ dictionary access
```

A 6-digit TOTP code must never be used directly as the file encryption key. It is only a second factor that authorizes or helps unwrap high-entropy key material.

## Two-Factor Decompression

The system behaves like decompression with 2FA.

```text
glyph stream alone        = not enough
dictionary alone          = not enough
TOTP alone                = not enough
encrypted payload alone   = not enough

glyph stream + dictionary + valid time gate + payload key = unfold
```

## Relationship to JORKI

JORKI currently represents the file as queryable state.

GE² adds a gated unfold layer:

```text
JORKI index packet
→ glyph/dictionary compression
→ encrypted envelope
→ public query-safe receipt
→ time-gated decode
→ full JORKI query session
```

Pre-decode:

```text
/meta
/capabilities
/public_receipt
/safe_preview
```

Post-decode:

```text
/summary
/search
/chunk
/query/sql
/raw if permitted
```

## Relationship to Antonymified File Receipts

Antonymification produces non-consumable preview.

GE² adds recoverable payload control.

```text
Antonymification = priceable non-seeing
GE²              = authorized unfolding
```

Together:

```text
visible blur + sealed payload + gated decoder + receipt
```

## Relationship to BlurHash64

BlurHash64 defines disclosure levels.

GE² uses those levels:

- Level 1–5: public blur / safe preview
- Level 6: public receipt
- Level 7: partial encrypted chunks
- Level 8: encrypted full body
- Level 9: full body after authorized decode

## Relationship to OverLanguage

OverLanguage can compile a file/workflow into a GE² envelope.

Example:

```text
overprogram EnigmaExport {
  object:
    □ = source_file

  encode:
    Γdict(□)

  protect:
    AEAD(payload_key, Γdict(□))

  gate:
    recipient + time_window + policy

  preview:
    antonymified_blur

  receipt:
    H□ Æ Hpacket Æ Rpolicy Æ Tgate

  output:
    packet.glyphpack
}
```

## Master Glyph

```text
□ → Γdict(□) → Czip → Ekey(Czip) Æ Rpublic Æ TOTP → ◎unfold
```

Plain English:

A file becomes dictionary-glyph encoded, compressed, encrypted, receipt-bound, and only unfolds when the time-gated decoder authorizes it.

## .glyphpack Format

```text
.glyphpack
├── packet.glyph          public compressed glyph packet
├── manifest.json         file type, size class, hash commitments
├── receipt.json          source hash, packet hash, policy hash
├── preview.json          safe low-fidelity preview
├── decoder.enc           encrypted dictionary or dictionary pointer
├── policy.json           expiry, buyer, query rights
├── merkle_root.txt       verification root
└── ciphertext.bin        encrypted compressed payload, optional by mode
```

## Commands

```text
glyphlock pack <file> --policy policy.json --dict dict.json --out file.glyphpack
glyphlock inspect file.glyphpack
glyphlock authorize file.glyphpack --recipient <id> --time-window now
glyphlock open file.glyphpack --auth current-session
glyphlock query file.glyphpack "find login function"
glyphlock revoke file.glyphpack --session <id>
glyphlock verify file.glyphpack
```

## Query-Only Mode

Full reconstruction should not always be required.

Modes:

```text
preview_only     = safe outer layer only
query_only       = decoded index available, raw body blocked
chunk_access     = selected chunks available
full_unfold      = full file reconstruction allowed
```

JORKI should default to `query_only` for LLM sessions.

## Issuer-Controlled Dictionary

The issuer controls:

- dictionary version
- token placement rules
- operator meanings
- glyph order
- segment boundaries
- time unlock policy
- query rights
- revocation policy

But the issuer should not assume the algorithm remains secret. The implementation must remain secure even when the public codec specification is known.

## Leak Tests

Each envelope should be tested for leakage before publication.

Questions:

- Can the preview reconstruct the file?
- Can the glyph stream reveal secrets without the decoder?
- Does the dictionary leak too much if exposed?
- Does the packet contain raw snippets?
- Are chunks encrypted?
- Can SQL expose full content before authorization?
- Can an expired time code be replayed?
- Does revocation kill all post-decode endpoints?

## Production Gates

The primitive is production-ready only when:

- payload encryption uses authenticated encryption
- file key is random and high entropy
- TOTP is only a second factor, not the file key
- IV/nonce uniqueness is enforced
- dictionary access is policy-gated
- public preview passes leakage tests
- receipt binds public metadata as AAD
- decode events are logged
- revocation is enforced
- query-only mode works without raw-body exposure
- recovery path is documented

## Final Product Claim

> A JORKI Enigma Envelope makes a file economically visible before it is technically consumable, then makes full reconstruction conditional on a time-bound decoder capability.

## Final Law

```text
G alone → priceable blur
G + D + Kt + key → unfold
G + D + Kt + key + R → accountable access
```

The file is not absent. It is split across packet, dictionary, key, time, policy, and receipt.
