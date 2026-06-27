# TrackGlyphKit: Trackpad Glyph Input and Gesture Receipts

## Status

This document defines a glyph-based trackpad input layer for Reality Compiler, MirrorMind, Layer4Meter, and OverLanguage.

Working name:

> **TrackGlyphKit**

Product phrase:

> Turn trackpad motion into intent language.

## Thesis

The trackpad should not be treated only as a pointer or a small list of system gestures.

A trackpad can be treated as a continuous glyph emitter.

Current OS-level interaction typically collapses rich input into a small action vocabulary:

```text
tap
click
scroll
swipe
pinch
spread
rotate
force click
mission-control gesture
```

TrackGlyphKit instead compiles micro-gesture evidence into symbolic sequences:

```text
touch topology + pressure + motion + zone + rhythm + velocity → glyph stream
```

The result is a gesture language that can be parsed, replayed, shared, audited, and bound to receipts.

## Official Apple Boundary

Apple already publicly documents Multi-Touch gestures on Mac, including tap, two-finger secondary click, smart zoom, two-finger scroll, pinch zoom, rotation, two-finger page swipe, right-edge Notification Center swipe, three-finger drag, three-finger lookup/data detectors, thumb-plus-three-finger desktop/app gestures, and four-finger Mission Control / App Exposé / full-screen-space gestures.

Apple also states that these gestures require a Magic Trackpad or built-in Multi-Touch trackpad, and that if a trackpad supports Force Touch, the user can also force click and get haptic feedback.

TrackGlyphKit does not replace Apple gestures. It builds an app-level symbolic layer above available touch/gesture events.

## What Changes

Traditional model:

```text
user moves finger → OS recognizes gesture → app receives action
```

TrackGlyph model:

```text
user performs micro-motion → TrackGlyphKit emits glyph stream → parser maps glyph sentence to intent / receipt / command
```

The breakthrough:

```text
binary events become gesture language
```

## Glyph Axes

### 1. Topology

```text
◌  single finger
◍  two fingers
⬡  three fingers
⬢  four fingers
⬣  palm / broad contact
```

### 2. Pressure

```text
·   hover / near-zero contact
-   light touch
◉   press
◎   deep press
●   force touch
```

Boundary:

- actual pressure availability depends on hardware and exposed APIs
- Force Touch-capable hardware can expose pressure-like interactions, but V1 must gracefully degrade to tap/click/hold when pressure data is unavailable

### 3. Motion

```text
→   right
←   left
↑   up
↓   down
↻   clockwise arc
↺   counter-clockwise arc
⇄   horizontal oscillation
⇅   vertical oscillation
∿   tremor / uncertainty
⌁   flick / high velocity
⋯   drag / low velocity continuation
```

### 4. Spatial Zone

```text
⌖   center
◧   left edge
◨   right edge
◩   top edge
◪   bottom edge
⬔   corner
```

### 5. Temporal Rhythm

```text
⋅   tap
–   hold
━   long hold
⋯   continuous
♪   rhythmic pattern
```

## Compound Glyphs

Examples:

```text
◌◉→      = one finger, press, move right
◍◎⇄      = two fingers, deep pressure, horizontal contraction/expansion
◌●━      = one finger, force hold
⬡-↑⌁     = three fingers, light upward flick
◧◌◉      = one-finger press on left edge
◨◍-      = two-finger light contact on right edge
```

Compound glyphs become gesture sentences:

```text
◌◉→  ◍◎⇄  ⬡-↻
```

Decoded:

```text
select → zoom/scale → rotate/orient
```

## Capability Unlocks

### 1. Gesture Command Language

Trackpad input becomes app-specific command syntax.

```text
◌◉→   = select mode
◍◎⇄   = zoom / inspect mode
⬡-↻   = rotate / reorient mode
◌●♪   = command palette
```

### 2. Pressure-Graded Fidelity Ladder

A single gesture can expose different levels of action.

```text
L0: ·◌   preview
L1: -◌   select
L2: ◉◌   activate
L3: ◎◌   inspect / expand
L4: ●◌   full context / force action
```

This mirrors the BlurHash64 / SonicGlyph64 idea: pressure becomes a disclosure or commitment level.

### 3. Chord Input

Multiple fingers in different zones become chords.

```text
◧◌◉ + ◨◍- = split view / dual-pane mode
⬔◌● + ⬔◍● = capture / screenshot region
```

Trackpad input becomes closer to a piano than a mouse.

### 4. Temporal Glyph Sequences

Sequences become macros.

```text
record glyph stream → replay → parameterize → share
```

Use cases:

- repeat design transformations
- replay demo steps
- reproduce agent UI navigation
- teach another user a gesture recipe
- bind user input to an audit trail

### 5. Velocity-Encoded Intent

```text
⌁ = throw / dismiss / commit quickly
⋯ = place / position / carefully drag
∿ = hesitation / uncertainty / suggest tooltip
```

The LLM can interpret hesitation as a support signal rather than treating all cursor motion equally.

### 6. Zone-Based Shortcuts

```text
⌖ center = current app / canvas
◧ left   = navigation
◨ right  = inspector
◩ top    = menu / global controls
◪ bottom = dock / timeline
⬔ corner = system / capture / emergency
```

The trackpad becomes a spatial control surface.

### 7. Gesture Receipts

TrackGlyphKit can emit a receipt for a gesture session.

```text
TRACKGLYPH RECEIPT

Session: 2026-06-27 11:04:22 ET
App: MirrorMind
Mode: TV-Safe Presentation
Glyph Stream: ◌-→ ◌◉→ ◍◎⇄ ◌●━
Decoded: light swipe, select, inspect, force-confirm
Hash: sha256:...
Claim: user intentionally selected window-only presentation
```

This connects directly to Layer4Meter.

Layer4Meter records what changed on the machine.

TrackGlyphKit records what the user physically expressed.

## Reality Compiler Integration

```text
TrackGlyphKit → OverLanguage intent event → Agent Runtime action → Layer4Meter receipt → LambdaReceipt
```

Example:

```text
◌◉→  ◍◎⇄  ◌●━
```

Compiles to:

```text
select artifact → inspect proof → confirm export
```

## MirrorMind Integration

TrackGlyphKit can become the private presentation control surface.

```text
left edge swipe     = previous proof card
right edge swipe    = next proof card
deep press          = reveal receipt detail
force hold          = approve TV-safe output
two-finger pinch    = compact / expand proof wall
three-finger flick  = emergency hide private screen
```

The product line:

> Before you mirror, know what you are showing. While you mirror, control it without leaking the desktop.

## Public Product Boundary

Do not claim:

- full private Apple trackpad internals
- guaranteed pressure data on all devices
- replacement of macOS gestures
- operating-system-level remapping without permissions
- mind reading
- universal gesture semantics across all apps

Claim:

- app-level glyph encoding for available gesture/touch signals
- private gesture receipts
- symbolic macro/replay layer
- TV-safe presentation control
- accessibility-friendly gesture alternatives
- user-intent telemetry for proof workflows

## MVP Scope

V1 should implement:

1. Swift/AppKit sample app.
2. Capture available trackpad gesture events.
3. Normalize into glyph axes: topology, motion, zone, temporal rhythm.
4. Add pressure axis only where exposed and supported.
5. Emit JSONL glyph stream.
6. Render live glyph transcript.
7. Map 5 glyph sequences to commands.
8. Export TrackGlyph receipt.
9. Integrate one command with MirrorMind or Reality Wall.

## V1 Commands

```text
trackglyph start --app MirrorMind
trackglyph record --seconds 30
trackglyph decode session.trackglyph.jsonl
trackglyph export --format receipt
trackglyph verify receipt.trackglyph
```

## Receipt Format

```text
.trackglyph
├── manifest.json
├── glyph_stream.jsonl
├── decoded_events.jsonl
├── command_map.json
├── claims.jsonl
├── shard_hashes.json
├── merkle_root.txt
└── report.md
```

## Example JSONL Event

```json
{
  "t": "2026-06-27T11:04:22.104-04:00",
  "topology": "one_finger",
  "pressure_class": "press",
  "motion": "right",
  "zone": "center",
  "tempo": "drag",
  "glyph": "◌◉→⋯⌖",
  "confidence": 0.88
}
```

## Accessibility Angle

TrackGlyphKit can help users who struggle with precise pointer movement by allowing:

- pressure-pattern commands
- zone commands
- rhythm commands
- macro gestures
- confirmation gestures
- undo-by-replay
- gesture recipes

This should be positioned as an accessibility-adjacent interaction layer, not as a replacement for Apple accessibility features.

## Research Adjacent

Recent interaction research supports the broader direction of turning touch-like behavior into richer interaction models. For example, TouchFusion uses multimodal wristband sensing to enable touch interactions on nearby surfaces, basic trackpad-like interactions, and adaptive interfaces. TrackGlyphKit is simpler: it starts with existing Mac trackpad signals and compiles them into an app-level glyph stream.

## Final Law

```text
The binary trackpad gives events.
The glyph trackpad gives language.
```

Or:

```text
Pointer movement shows where the user went.
TrackGlyph shows what the user meant.
```
