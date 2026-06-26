# JORKI: 1GB LLM File Gateway Readiness and Superposition Clipboard Protocol

## Status

This document is a sanitized readiness specification extracted from the Hypercomplex ML Pipeline build transcript. The raw transcript contains local build history and token-like strings and must not be committed directly.

JORKI is the file-access substrate for AI-native work. It lets an LLM inspect a large local artifact through a compact queryable state object rather than by receiving the whole file.

Core thesis:

> JORKI does not transfer files to LLMs. It transfers queryable state.

A large local file becomes an LLM-readable object through a compact index, cryptographic identity, chunk retrieval, SQL/search endpoints, clipboard session encoding, and explicit revocation.

## Product Positioning

Brand: **Jorki**

Tagline:

> Move files. Not friction.

Sharper technical tagline:

> Not file transfer. Context transfer.

JORKI is not Dropbox, WeTransfer, or another RAG demo. It is an AI file gateway: a large file emits a query surface so an LLM can inspect only what it needs.

## System Boundary

A Hugging Face Space cannot directly read a file that remains only on a Mac by URL alone. One of the following must be true:

1. A local companion serves authorized byte ranges or chunks.
2. A compact uploaded index contains enough safe metadata, semantic chunks, and previews for the LLM to answer without the original file.
3. A hybrid mode uploads a compact index first and later authorizes minimal byte-range retrieval from the local machine.

The production-safe claim is therefore:

> Local file stays local or partially abstracted; JORKI uploads only the queryable representation required for the selected disclosure level.

## Architecture

```text
Finder
  → right click
  → JORKI Quick Action
  → local engine
  → compact semantic index
  → hash/Merkle identity
  → Hugging Face Space query gateway
  → LLM selective retrieval
```

Primary components:

- Finder Quick Action: right-click entry point.
- Swift/AppKit menu bar app: dashboard, active sessions, speed meter, revocation controls.
- C++ local engine: memory-mapped scanning, semantic chunking, function extraction, Merkle hashing, SQLite index emission.
- SQLite index: compact queryable file state.
- Hugging Face Space: public/private query gateway exposing health, meta, summary, search, chunk, SQL, GraphQL/MCP-style endpoints.
- Clipboard protocol: one pasteable object carrying URL, file ID, merkle root, capabilities, expiry, and query rules.

## File State Primitive

```text
File → Local semantic index → Hash/Merkle receipt → Remote query gateway → LLM selective retrieval
```

The file does not become the URL. The URL points to a controlled query surface derived from the file.

## Superposition Clipboard Object

The clipboard object should contain:

```text
JORKI_URL
FILE_ID
MERKLE_ROOT
CAPABILITIES
QUERY_CONTRACT
EXPIRY
AUTH_POLICY
REVOCATION_URL
```

Example shape:

```json
{
  "kind": "jorki.session.v1",
  "url": "https://<space>.hf.space/meta/<file_id>",
  "file_id": "abc123...",
  "merkle_root": "sha256:...",
  "capabilities": ["meta", "summary", "search", "chunk", "sql", "mcp"],
  "query_contract": {
    "download_full_file": false,
    "sql": "read_only_select",
    "chunk_policy": "minimum_necessary",
    "verify_merkle": true
  },
  "expiry": "session_or_timestamp",
  "auth_policy": "bearer_or_signed_session",
  "revoke": "https://<space>.hf.space/revoke/<file_id>"
}
```

## LLM Instructions

When an LLM receives a JORKI session URL, it should follow this protocol:

```text
Do not download the whole file.
Read /meta first.
Read /summary second.
Use /search for candidate locations.
Use /chunk only for necessary ranges.
Use /query/sql only for read-only SELECT queries.
Verify merkle_root and receipt fields when available.
Stop after the minimum context needed to answer.
Respect expiry and revocation state.
```

## Verified Production-Style Behaviors From Transcript

The uploaded transcript records a build path where the following behaviors were reported as verified:

- HF Space health endpoint.
- Upload endpoint.
- Metadata endpoint.
- Summary endpoint.
- Search endpoint.
- Chunk endpoint.
- SQL query endpoint.
- MCP-style manifest/query endpoint.
- Revocation behavior.
- Post-revoke not-found behavior.
- Finder Quick Action installed.
- C++ engine compiled.
- Swift/AppKit menu bar app compiled or ran.
- Indexing and upload timing measurements.

These are transcript claims and should be revalidated in a fresh production-readiness run.

## 1GB Readiness Truth Table

| Requirement | Status | Production Gate |
|---|---:|---|
| Index 1GB file locally | Needs hard validation | Run real 1GB file, record wall time, peak RAM, output index size. |
| Upload only compact index | Partially demonstrated | Confirm index contains no unsafe raw secret material. |
| HF Space health/meta/search/chunk/SQL | Transcript says verified | Re-run all endpoints on current Space build. |
| Revocation | Transcript says verified | Revoke session, confirm all endpoints return 404/403. |
| Persistence | Must verify | Restart Space; confirm session survives only if persistent storage is attached. |
| Auth | Must verify | Upload without auth must fail; query permissions must match session policy. |
| Token handling | Unsafe in raw transcript | Rotate leaked tokens; move secrets to HF Space settings. |
| Index leakage | Not solved by default | Run adversarial leakage tests. |
| MCP compatibility | Transcript says endpoint exists | Validate against actual MCP client expectations. |
| SQL safety | Must enforce | Read-only SELECT, table allowlist, timeout, row limit. |

## Production Readiness Test

A serious 1GB validation must use one real file and produce a receipt:

1. Select a real 1GB+ file.
2. Generate JORKI index locally.
3. Record input file size.
4. Record index size.
5. Record indexing wall time.
6. Record peak memory.
7. Record CPU utilization.
8. Upload index to HF Space.
9. Record upload size and upload time.
10. Paste session object to an LLM.
11. LLM reads `/meta`.
12. LLM reads `/summary`.
13. LLM performs at least three `/search` queries.
14. LLM reads only necessary `/chunk` ranges.
15. LLM performs at least one safe SQL query.
16. Verify merkle root in session receipt.
17. Revoke session.
18. Confirm post-revoke endpoints return not found or forbidden.
19. Restart Space.
20. Confirm persistence behavior is expected.

## Endpoint Contract

Minimum endpoint set:

```text
GET  /health
POST /upload
GET  /meta/{file_id}
GET  /summary/{file_id}
GET  /search/{file_id}?q=...
GET  /chunk/{file_id}/{chunk_id}
GET  /chunks/{file_id}
POST /query/sql/{file_id}
GET  /capabilities/{file_id}
GET  /mcp
POST /mcp/query
POST /revoke/{file_id}
```

Optional endpoint set:

```text
POST /graphql
GET  /auth/status
GET  /sessions
GET  /analytics/{file_id}
POST /permissions/{file_id}
```

## SQL Safety Contract

SQL access must be constrained:

- allow only `SELECT`
- reject semicolons when multiple statements are detected
- deny `ATTACH`, `DETACH`, `PRAGMA`, `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`
- enforce row limit
- enforce timeout
- allowlist exposed tables
- log query hash, not necessarily full query text if sensitive

## Index Leakage Risk

Uploading an index is safer than uploading a full 1GB file, but it is not automatically safe.

The index may leak:

- filenames
- paths
- function names
- URLs
- emails
- IPs
- secrets appearing in previews
- line snippets
- semantic chunks
- unique identifiers
- business logic

Mitigation:

- redact secrets before upload
- preview truncation
- field-level disclosure policy
- private sessions by default
- signed session URLs
- short expiry
- explicit revoke
- index leakage tests

## Security Hardening

Token-like strings appeared in the raw transcript. Treat them as compromised.

Required actions:

1. Revoke leaked tokens.
2. Create a new fine-grained token scoped only to the JORKI Space.
3. Store secrets only in Hugging Face Space secrets or local keychain/env.
4. Never commit tokens to GitHub, Space README, logs, or transcript files.
5. Add secret scanning before release.
6. Add API auth to uploads and privileged endpoints.
7. Add rate limits.
8. Add per-session expiry.
9. Add revocation receipts.

## Persistence Boundary

Default Hugging Face Space disk is ephemeral. Long-lived sessions require attached persistent storage or an external registry.

Production options:

- attached Hugging Face Storage Bucket mounted into the Space
- external object storage
- signed session registry backed by durable database
- deliberately ephemeral sessions with explicit expiry labeling

Do not claim persistent sessions unless persistence is verified after a Space restart.

## Landing Page Copy

Hero:

> JORKI
>
> Move files. Not friction.
>
> The fastest way to send, host, and share queryable file context from your own Hugging Face Space.

Technical hero:

> Not file transfer. Context transfer.
>
> Paste one URL. An AI can explore large artifacts through metadata, search, SQL, and chunks without downloading the whole file.

CTA:

```text
[Start Uploading] [Live Demo] [API Docs]
```

## Product Claims That Are Safe

Safe:

- JORKI creates queryable file state.
- JORKI can upload a compact index instead of a full file.
- JORKI can expose metadata, search, chunk, SQL, and MCP-style query surfaces.
- JORKI can support revocable sessions.
- JORKI can reduce unnecessary full-file transfer.

Avoid without proof:

- “1GB verified” unless a real 1GB receipt exists.
- “persistent” unless restart persistence is tested.
- “secure” without auth, rate limits, and leakage tests.
- “no upload” if the index contains reconstructable chunks or previews.
- “LLM can inspect local file by URL alone” without local serving or uploaded representation.

## Next Implementation Tickets

1. Run 1GB readiness test.
2. Add JORKI session receipt format.
3. Add SQL safety allowlist.
4. Add index leakage scanner.
5. Add Space restart persistence test.
6. Add revocation receipt.
7. Add MCP client compatibility test.
8. Add session clipboard schema.
9. Add landing page safety language.
10. Add token rotation checklist.

## Final Law

```text
File transfer moves bytes.
JORKI transfers queryability.
```

JORKI becomes serious when every URL can answer four questions:

1. What file state does this represent?
2. What can the LLM safely query?
3. What proof binds the query surface to the source artifact?
4. How can access be revoked?
