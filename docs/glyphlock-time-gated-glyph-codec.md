# GlyphLock: Time-Gated Glyph Dictionary Codec

## Status

This document defines the codec/access primitive that sits between JORKI, Antonymified File Receipts, BlurHash64, and OverLanguage.

Working names:

- **GlyphLock**
- **JORKI Enigma Envelope**
- **Time-Gated Glyph Codec**
- **Glyph Enigma Envelope**

Best formal name:

> **Time-Gated Glyph Dictionary Encoding**

## Thesis

A file can be made economically visible before it is technically consumable by splitting its meaning across a visible glyph packet and a time-gated decoder.

Core sentence:

> We are not hiding the file. We are splitting its meaning across a visible glyph packet and a time-gated decoder.

Sharper sentence:

> The file becomes a puzzle whose solution is not intelligence, but authorization.

## Primitive

```text
File → Glyph Projection → Puzzle Packet → Time-Keyed Decoder → Full Unfolded File
```

Or:

```text
□ → Γ(D,Kt) → ◇blur
◇blur + D + Kt + P = □◎
```

Where:

```text
□      = original file
Γ      = glyph codec transform
D      = decoder dictionary / rulebook
Kt     = time-derived key or time-gated unlock factor
P      = issuer policy
◇blur  = public low-fidelity glyph packet
□◎     = verified unfolded file
```

## Key Correction

Obscurification alone does not compress.

Compression happens when the issuer and decoder share or later unlock side information: a dictionary, rulebook, codebook, seed, model, or key schedule.

Therefore:

```text
G alone                 ≠ File
G + confusion           ≠ Security
G + D + Kt + Policy      = Unfold
```

The serious mechanism is:

> compression with private side information plus time-gated decoder access.

## Architecture

### Layer 1: Public Glyph Packet

A small, portable, partially interpretable object.

Contains:

- file class
- size class
- capability hints
- safe previews
- operator traces
- hash commitments
- Merkle root
- policy flags
- expiry metadata
- receipt pointer

Pre-decode state:

```text
priceable blur
```

The public packet should be interpretable enough to route, price, verify, or decide whether to request access, but not enough to reconstruct or consume the original file.

### Layer 2: Private Decoder Dictionary

The issuer-controlled mapping table.

Contains:

- glyph meanings
- operator placement rules
- token dictionary
- semantic segment dictionary
- reconstruction rules
- chunk transforms
- versioned codec rules
- optional model/seed references

This is the Enigma book. Without it, the glyph packet remains only partially meaningful.

### Layer 3: Cryptographic Envelope

The payload must be protected by real cryptography, not by custom encoding alone.

Recommended construction:

```text
payload_key = random 256-bit key
compressed_payload = glyph_codec(file, dictionary)
ciphertext = AEAD_encrypt(payload_key, compressed_payload, public_receipt_as_AAD)
wrapped_key = wrap(payload_key, recipient_or_session_key)
```

The algorithm should be public. Security should depend on keys, not secrecy of the algorithm.

### Layer 4: Time/Auth Gate

The time factor is not the file encryption key.

The time factor authorizes release or unwrapping of a high-entropy key.

Required factors:

```text
recipient identity
+ issuer policy
+ session key
+ time window or TOTP-style factor
+ wrapped payload key
```

TOTP-style 2FA is useful as an authorization factor, but a short one-time code is not strong enough to serve as the file encryption key.

### Layer 5: Receipt + Revocation

Every decode or query event emits a receipt.

Receipt records:

- packet hash
- dictionary hash
- encrypted body hash
- decoded session ID
- issuer policy hash
- recipient identity hash
- time window
- query scope
- revocation status
- result hash

## Object Format

Suggested extension:

```text
.glyphpack
```

Suggested directory shape:

```text
packet.glyphpack/
├── packet.glyph          public compressed glyph packet
├── manifest.json         file type, size class, codec version, capability list
├── receipt.json          source hash, packet hash, policy hash
├── preview.json          low-fidelity safe preview
├── decoder.enc           encrypted dictionary / rulebook
├── policy.json           expiry, buyer, query rights, decode rights
├── ciphertext.bin        encrypted compressed payload or encrypted index
├── wrapped_key.json      recipient/session wrapped payload key
├── merkle_root.txt       verification root
└── audit.jsonl           decode/query events
```

## Access States

```text
G alone              → priceable blur
G + public receipt   → verifiable blur
G + D                → interpretable structure
G + D + Kt           → reconstructable/queryable file
G + D + Kt + R       → accountable access
```

Where:

```text
G  = glyph packet
D  = decoder dictionary
Kt = time/auth gated key factor
R  = receipt
```

## Disclosure States

### Pre-Decode

Visible to buyer, LLM, or verifier:

- class
- shape
- schema hints
- capability hints
- proof hooks
- hash/Merkle commitments
- oracle options
- access policy
- expiry

Not visible:

- full raw bytes
- full source text
- complete dataset rows
- secrets
- reconstructable implementation
- private dictionary
- payload key

### Post-Decode

Available only after authorized unfold:

- full query surface
- chunks
- semantic index
- raw body if permitted
- verified receipt chain
- reconstruction proof

## Relation to Existing Stack

```text
BlurHash64        = fidelity ladder
Antonymification  = non-consumable preview
JORKI             = query gateway
GlyphLock / GE²   = time-gated glyph codec envelope
OverLanguage      = workflow grammar
Layer4Meter       = compute receipt
Glyph ML          = policy layer
```

GlyphLock is the codec/access layer that lets JORKI carry more than a normal index while still preventing unauthorized consumption.

## Master Glyph

```text
□ → Γdict(□) → Czip → Ekey(Czip) Æ Rpublic Æ TOTP → ◎unfold
```

Plain English:

A file becomes dictionary-glyph encoded, compressed, encrypted, receipt-bound, and only unfolds when the time-gated decoder authorizes it.

## Security Rules

```text
Codec ≠ Security
Compression ≠ Encryption
Obscurification ≠ Proof
TOTP ≠ File Key
```

Use the glyph/dictionary layer for compactness and controlled interpretability.

Use cryptography for confidentiality and integrity.

Use receipts for accountability.

Use time gates for authorization windows.

## Threat Model

### Attacker Has Public Packet Only

Expected result:

- can identify class/capabilities
- can verify public commitment
- cannot reconstruct file
- cannot query full content

### Attacker Has Public Packet + Codec Spec

Expected result:

- still cannot reconstruct without dictionary/key
- can understand general grammar
- cannot derive private decoder

### Attacker Has Public Packet + Dictionary But No Key

Expected result:

- may understand structure
- cannot decrypt full payload
- cannot verify authorized unfold

### Attacker Has TOTP Code Only

Expected result:

- cannot decrypt file
- cannot derive payload key
- may only authorize a broker interaction if other factors match

### Attacker Has Payload Key

Expected result:

- can decrypt payload during valid scope
- receipt should record or detect access where possible
- revocation should prevent future gateway access, though already downloaded plaintext cannot be clawed back

## Compression Boundary

GlyphLock can reduce size when:

- workflows have repeated structure
- both sides share a dictionary
- operator placement encodes common patterns
- semantic segments repeat
- file classes have known templates
- payload uses normal lossless compression after glyph encoding

GlyphLock will not magically compress random high-entropy data unless side information, dictionary structure, or external storage carries the missing information.

## Hosting Boundary

The statement “the file does not need to be hosted when it is not observed” must be read operationally, not physically.

Correct version:

> The raw file does not need to be hosted continuously. The system can host a receipt, packet, encrypted payload, dictionary reference, or query surface, and materialize full access only after authorization.

If no component stores the raw file, encrypted file, sufficient encoded payload, or reachable local source, then the file cannot be reconstructed.

## JORKI Integration

JORKI can expose a GlyphLock session as:

```text
JORKI_URL + FILE_ID + GLYPH_PACKET_HASH + MERKLE_ROOT + DECODER_POLICY + EXPIRY
```

LLM instruction:

```text
Read public preview.
Do not attempt full decode unless authorized.
Use search/chunk only within current capability scope.
Request time-gated unfold if full query access is needed.
Verify receipt after unfold.
```

## MVP

### Encode

```text
glyphlock pack input.file --policy policy.json --recipient recipient_id
```

Outputs:

```text
packet.glyphpack
```

### Preview

```text
glyphlock preview packet.glyphpack
```

Returns:

- class
- capability list
- safe preview
- hash commitments
- expiry
- decode policy

### Unlock

```text
glyphlock open packet.glyphpack --auth current-session
```

Requires:

- recipient authorization
- policy acceptance
- valid time window
- key unwrap

### Query

```text
glyphlock query packet.glyphpack "find login function"
```

Allowed only after policy permits query access.

### Revoke

```text
glyphlock revoke packet.glyphpack --session SESSION_ID
```

Emits revocation receipt.

## Implementation Plan

V1:

- define `.glyphpack` manifest
- build static dictionary codec
- add ordinary compression stage
- encrypt payload with AEAD
- wrap payload key
- implement preview command
- implement unlock command
- emit receipt JSON

V2:

- add JORKI gateway integration
- add query-only decode mode
- add revocation endpoint
- add audit log
- add policy-bound chunk access

V3:

- add rotating dictionaries
- add recipient-specific dictionaries
- add time-window key broker
- add hardware-bound local keychain support
- add leakage tests

V4:

- add selective disclosure proofs where actual verifier exists
- add OverLanguage compilation target
- add Glyph ML policy supervisor

## Acceptance Criteria

The MVP is complete when:

- a file can be packed into `.glyphpack`
- public preview is useful but non-reconstructive
- the payload cannot be read without authorization
- the dictionary is versioned and hash-bound
- the packet has a Merkle/source commitment
- the payload uses authenticated encryption
- the time factor is treated as authorization, not as the encryption key
- a decode receipt is emitted
- revocation prevents future gateway access
- already-downloaded plaintext is explicitly out of revocation scope

## Product Claim

> GlyphLock makes a file economically visible before it is technically consumable, then makes full reconstruction conditional on a time-bound decoder capability.

## Final Law

```text
G alone → priceable blur
G + D + Kt → unfold
G + D + Kt + R → accountable unfold
```

Where the missing meaning is not guessed. It is authorized.
