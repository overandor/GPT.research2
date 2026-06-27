# Reality Wall: Samsung TV, Sony TV, and Mac Connectivity Stack

## Status

This document defines the practical TV stack for Reality Compiler / ProofLens / JORKI / ClientPulse big-screen dashboards.

The product name is:

> **Reality Wall**

The TV is not the compute brain. The TV is the proof wall.

## Product Definition

Reality Wall is a 10-foot dashboard for provenance-backed AI-native work.

It displays:

- proof cards
- LambdaReceipts
- JORKI files
- SonicGlyph audio/video proofs
- ClientPulse KPIs
- receipt chain status
- experiment status
- live artifact ledger

## Platform Rule

Samsung TV and Sony TV should not be treated as the same native target.

```text
Samsung TV = Tizen Web App target
Sony TV    = Android/Google TV + Cast/IP-control target
Mac        = Swift controller / local proof engine
Backend    = Node / FastAPI / Rust service
Heavy proof/compression = WASM or server-side module
```

## Samsung TV Stack

Best default:

```text
Language: TypeScript
UI: React
Styling: CSS
Runtime: Tizen Web App
Build: Vite / React build
Packaging: Tizen Studio + TV Extension
Testing: TV Simulator, TV Emulator, real Samsung TV, Web Inspector
Performance module: C/C++ → WebAssembly when needed
```

Samsung Smart TV development is centered around Tizen tooling, Web Applications, TV SDK, TV Simulator, TV Emulator, Web Inspector, and Tizen packaging.

### Why TypeScript + React

TypeScript is the best Samsung TV default because TV bugs are expensive to debug:

- focus state errors
- remote-control navigation errors
- playback state errors
- API shape errors
- device/version differences

React is acceptable if the app is kept lightweight and optimized for TV.

### Samsung Performance Path

Use WebAssembly only for heavy local modules:

- proof compression
- receipt verification
- hash/Merkle verification
- audio fingerprinting
- local rendering transforms

Samsung documents WebAssembly as a way to run C/C++ on the web at near-native speed, alongside JavaScript, and says Samsung smart devices support WebAssembly from Tizen 5.5 / 2020 models onward.

## Sony TV + Mac Stack

Best production stack:

```text
Mac controller: Swift / SwiftUI
Sony TV receiver: Kotlin Android TV app when Sony runs Google TV / Android TV
Connectivity bridge: TypeScript / WebSocket / Google Cast
Device control: Sony IP control / REST API where supported
Media transport: Cast, HLS, DASH, WebRTC depending on use case
Backend: Node / FastAPI / Rust
```

### Why Swift On Mac

Swift is the native choice for a Mac controller app because it is Apple’s language for Apple platforms, safe by design, fast, and interoperable with Objective-C/C++.

Mac responsibilities:

- local receipt generation
- JORKI indexing control
- file picking
- Layer4Meter status
- local network discovery
- TV session control
- pairing/auth state
- proof push to TV

### Why Kotlin On Sony TV

If the Sony TV runs Android TV / Google TV, use Kotlin with Android TV UI patterns.

Google’s Android TV docs emphasize that TV apps run locally on TV devices but need a different interaction model from phones/tablets: design for viewing from 10 feet away and directional-pad/select-button navigation. Modern UI should use Compose for TV; Leanback UI toolkit is deprecated.

### Why TypeScript For Bridge

Use TypeScript for the bridge because Google Cast supports Sender apps on Android, iOS, and Web, while Receiver apps can be Web Receivers or Android TV Receivers.

Reality Wall should use a Custom Receiver or Android TV Receiver if it needs:

- custom UI
- authentication
- analytics
- custom messages
- receipt synchronization
- proof-specific business logic

Google’s Default Media Receiver is acceptable only for learning or very limited playback, not for production proof dashboards.

## Sony BRAVIA Control

For compatible Sony BRAVIA professional displays, Sony documents IP-network control interfaces including REST API, IRCC-IP, Simple IP Control, Serial Control, and Cloud API.

The REST API allows display control over local IP networking using HTTP communication with JSON-RPC-compliant commands.

Use this for:

- power/status control
- input switching
- signage mode
- dashboard display orchestration
- multi-display walls

Do not treat consumer AirPlay behavior as the programmable foundation. Use Cast/IP control when reliability and automation matter.

## Unified Architecture

```text
Mac / Server
Swift + Node/FastAPI/Rust
  ├── Reality Compiler engine
  ├── JORKI file access
  ├── Layer4Meter receipts
  ├── ReceiptOS ledger
  ├── LambdaBase scoring
  └── WebSocket/Cast/API bridge
        ↓
TV Runtime
  ├── Samsung: Tizen Web App (TypeScript/React)
  └── Sony: Android TV/Kotlin or Cast Web Receiver
        ↓
Reality Wall UI
  ├── proof cards
  ├── receipt chain
  ├── artifacts
  ├── audio/video proof
  ├── KPIs
  └── live status
```

## 10-Foot UI Rules

TV UI must be designed for distance and remote control.

Rules:

- huge typography
- few buttons
- no tiny forms
- no dense tables by default
- remote arrows: up/down/left/right
- enter/select as primary action
- back as escape
- high contrast
- fast first paint
- memory-light rendering
- no hidden hover-only behavior

## Reality Wall MVP

Build the first version as a Samsung Tizen Web App because it is fastest to ship and easiest to iterate with TypeScript/React.

### Frontend

```text
TypeScript
React
CSS
Tizen Web APIs
Remote-control key handling
WebSocket client
```

### Backend

```text
Node or FastAPI
WebSocket events
Receipt API
Artifact API
JORKI session API
ClientPulse KPI API
```

### Data Flow

```text
Reality Compiler backend
→ receipt event
→ WebSocket broadcast
→ Reality Wall card update
→ TV displays proof state
```

### Screens

1. Live Proof Wall
2. Receipt Detail
3. JORKI File Session
4. SonicGlyph Audio/Video Proof
5. ClientPulse KPI Board
6. LambdaBase Value Board
7. System Health

## Platform Decision Table

| Need | Best Target |
|---|---|
| Fastest Samsung app | TypeScript + React + Tizen Web App |
| Samsung heavy local compute | C/C++ compiled to WebAssembly |
| Sony native TV app | Kotlin + Compose for TV |
| Sony/Mac media casting | Google Cast sender/receiver |
| Sony display control | Sony REST API / IP control where supported |
| Mac controller | Swift / SwiftUI |
| Cross-platform prototype | TypeScript web app |
| Backend API | Node / FastAPI / Rust |
| AI/proof heavy compute | Server-side or WASM, not TV-local inference |

## Avoid

Do not start with:

- Swift for Samsung TV UI
- Kotlin for Samsung TV UI
- Python on the TV
- forced AirPlay reverse engineering
- local TV inference as V1
- tiny desktop UI on a 10-foot display
- heavy proof computation on old TV hardware

## Final Recommendation

Default Reality Wall build:

```text
Samsung TV:
  TypeScript + React + Tizen Web App

Sony TV:
  Kotlin Android TV Receiver OR Cast Web Receiver

Mac:
  Swift controller

Bridge:
  TypeScript/WebSocket + Google Cast where supported

Backend:
  Node/FastAPI/Rust

Heavy modules:
  WASM or server-side Rust/C++
```

## Final Law

```text
TV = proof display
Mac/server = proof engine
Phone/Mac = controller
WebSocket/Cast/IP control = bridge
```

Reality Wall should not try to make the TV the AI brain. It should make the TV the undeniable wall of proof.
