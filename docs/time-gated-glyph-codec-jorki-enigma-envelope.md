# Time-Gated Glyph Codec: JORKI Enigma Envelope

## Status

This is the product-facing alias for the deeper GlyphLock specification.

Canonical technical spec:

```text
docs/glyphlock-time-gated-glyph-codec.md
```

Product-facing name:

```text
JORKI Enigma Envelope
```

Formal primitive:

```text
Time-Gated Glyph Dictionary Encoding
```

## Thesis

The file does not disappear when unobserved. The serious mechanism is that the file's consumable meaning is split across:

1. a visible glyph packet,
2. a private decoder dictionary,
3. a cryptographic payload key,
4. a time/session authorization factor,
5. an access receipt.

This means a public host such as GitHub or a Hugging Face Space does not need to host the raw file at rest. It can host only the puzzle surface: receipt, Merkle root, capability map, blurred preview, compressed glyph stream, encrypted decoder reference, and query policy.

The full file becomes technically consumable only when the decoder capability is activated.

## Pipeline

```text
File
→ semantic segmentation
→ glyph/operator dictionary encoding
→ lossless compression
→ authenticated encryption
→ public receipt / blurred preview
→ time-gated decoder authorization
→ full unfold / query mode
```

## Compression Boundary

Obscurification does not compress by itself.

Compression happens because repeated structure is replaced with shorter symbols, dictionary references, backreferences, or statistical codes. The dictionary, codebook, seed, or side information is part of the effective decompressor.

The public glyph packet alone is therefore not the file.

## Security Boundary

The codec is not the security layer.

The secure design is:

```text
payload_key = random 256-bit key

glyph_payload = Γdict(file)
compressed_payload = compress(glyph_payload)

ciphertext = AEAD_encrypt(
  key = payload_key,
  plaintext = compressed_payload,
  aad = public_receipt
)

unlock requires:
  recipient identity
  issuer policy
  valid time factor
  wrapped payload_key
```

A short TOTP-style code should not be the file encryption key. It should authorize release or unwrap of a high-entropy payload key.

## Object

```text
GE² = Glyph Enigma Envelope
```

```text
GE² {
  public_preview: antonymified / blurred / priceable
  glyph_payload: compressed symbolic token stream
  dictionary_id: hash of decoder dictionary
  merkle_root: source identity
  aad: public receipt bound to ciphertext
  encrypted_payload: AEAD(compressed glyph payload)
  wrapped_key: payload key locked to recipient/session/time
  time_policy: TOTP or signed time window
  decoder_policy: who may unfold, when, how often
  query_policy: full unfold, chunk-only, or query-only
  revocation: session kill switch
}
```

## Access Law

```text
G alone              → priceable blur
G + D                → interpretable structure
G + D + Kt           → reconstructable/queryable file
G + D + Kt + R       → accountable access
```

Where:

```text
G  = glyph packet
D  = decoder dictionary / rulebook
Kt = time/session key or gated authorization factor
R  = receipt
```

## Operational Superposition

Use superposition as an operational product metaphor, not a physics claim.

```text
pre-observation state  = priceable encrypted/queryable potential
observation event      = valid decoder capability
post-observation state = unfolded file/query surface
```

Correct statement:

> The raw file does not need to be hosted continuously. The system can host a receipt, packet, encrypted payload, dictionary reference, or query surface, then materialize full access only after authorization.

Incorrect statement:

> The file exists from nothing when observed.

If no component stores the raw file, encrypted file, sufficient encoded payload, reachable local source, or equivalent side information, the file cannot be reconstructed.

## `.glyphpack` MVP

```text
.glyphpack
├── packet.glyph
├── manifest.json
├── preview.json
├── receipt.json
├── dictionary.enc
├── payload.enc
├── policy.json
├── merkle_root.txt
└── access_log.jsonl
```

## Commands

```text
glyphlock pack input.file --policy policy.json --recipient recipient_id
glyphlock preview packet.glyphpack
glyphlock open packet.glyphpack --auth current-session
glyphlock query packet.glyphpack "find login function"
glyphlock revoke packet.glyphpack --session SESSION_ID
```

## Relation To The Stack

```text
BlurHash64        = fidelity ladder
Antonymification  = non-consumable preview
JORKI             = query gateway
GlyphLock / GE²   = time-gated glyph codec envelope
OverLanguage      = workflow grammar
Layer4Meter       = compute receipt
Glyph ML          = policy layer
```

## Final Law

```text
Compression = shared structure
Security = cryptographic key
Interpretability = public blur
Unfolding = time-gated decoder capability
Receipt = accountable observation
```

The file becomes economically visible before decode and technically consumable only after authorized unfold.
