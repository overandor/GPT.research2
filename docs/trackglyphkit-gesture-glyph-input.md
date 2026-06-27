# TrackGlyphKit: Gesture Glyph Input Layer for macOS

## Status

This document defines TrackGlyphKit: a Swift/AppKit framework that turns trackpad gestures into a symbolic glyph stream.

The idea is not to replace Apple gestures. The idea is to encode richer gesture traces into a programmable, interpretable, receipt-ready language.

## Product Definition

> TrackGlyphKit turns trackpad interaction from discrete events into symbolic gesture sentences.

Short line:

> The trackpad becomes a glyph instrument.

## Core Insight

Today the user-facing trackpad vocabulary is small:

```text
tap
click
secondary click
scroll
swipe
pinch
spread
rotate
force click
three-finger drag
Mission Control / App Exposé gestures
```

Apple documents Multi-Touch gestures such as tap, swipe, pinch, spread, scroll, rotate, three-finger drag, and four-finger Mission Control/App Exposé gestures. If a trackpad supports Force Touch, Apple also exposes force click and haptic feedback behavior.

TrackGlyphKit does not claim the OS lacks rich input. It claims most apps consume that input after it has already been collapsed into a small set of high-level gestures.

TrackGlyphKit preserves more structure:

```text
finger topology + zone + pressure + velocity + trajectory + rhythm + duration = glyph
```

## Public API Boundary

V1 must stay on public, supportable APIs.

Use:

- AppKit views
- NSGestureRecognizer classes
- NSEvent / NSTouch where publicly available
- pressure/force-click callbacks where available
- user-authorized app-local capture

Avoid in V1:

- private MultitouchSupport / MTDevice APIs
- global trackpad keylogging-style capture
- kernel extensions
- private event taps for hidden gesture data
- App Store-hostile reverse engineering

Correct V1 boundary:

```text
app-local gesture language
```

Not:

```text
global raw trackpad sniffer
```

## Gesture Glyph Alphabet

### Topology

```text
◌  single finger
◍  two fingers
⬡  three fingers
⬢  four fingers
⬣  palm / full hand / broad contact
```

### Pressure

```text
·  hover / no committed touch
-  light touch
◉  press
◎  deep press
●  force touch
```

### Motion

```text
→  right
←  left
↑  up
↓  down
↻  clockwise arc
↺  counter-clockwise arc
⇄  horizontal contraction/expansion
⇅  vertical contraction/expansion
∿  wave / tremor
⌁  flick / high velocity
⋯  drag / low velocity continuation
```

### Spatial Zone

```text
⌖  center
◧  left edge
◨  right edge
◩  top edge
◪  bottom edge
⬔  corner
```

### Temporal / Rhythm

```text
⋅  tap
–  hold
━  long hold
⋯  continuous
♪  rhythmic pattern
```

## Compound Glyphs

A gesture frame becomes a compact symbolic token.

Examples:

```text
◌◉→      single-finger press moving right
◍◎⇄      two-finger deep pinch/spread axis
◌●━      one-finger force long-hold
⬡-↑⌁     three-finger light upward flick
⬢-←      four-finger light left swipe
```

A session becomes a sentence:

```text
◌◉→  ◍◎⇄  ⬡-↻  ◌●━
```

Decoded:

```text
select / drag → zoom / scale → rotate / orient → inspect / confirm
```

## Why This Matters

### 1. Gesture Command Language

Apps can register glyph dictionaries:

```text
◌◉→     = select / scrub / move
◍◎⇄     = zoom region
⬡-↑⌁    = lift to overview
◌●━     = inspect / reveal context
♪●      = command palette
```

This turns the trackpad into an app-specific command grammar.

### 2. Pressure-Graded Fidelity

Pressure becomes a disclosure ladder:

```text
L0: ·◌  preview / hover
L1: -◌  select
L2: ◉◌  activate
L3: ◎◌  inspect / expand
L4: ●◌  full context / commit
```

Same zone + same movement + different depth = different semantic operation.

### 3. Chorded Input

Multiple fingers in different zones can create chord states.

Example:

```text
◧◌◉ + ◨◍- = split / compare / dual pane
⬔◌● + ⬔◍● = system capture / proof checkpoint
```

Treat this like a piano, not a mouse.

### 4. Temporal Gesture Sentences

A gesture stream can be:

- replayed
- searched
- macro-recorded
- attached to a receipt
- used as an intent transcript
- mapped to OverLanguage
- scored for hesitation/confidence

### 5. Velocity-Encoded Intent

```text
⌁  flick = throw / dismiss / commit fast
⋯  drag  = place / position / inspect slowly
∿  tremor = uncertain / ask for help / show tooltip
```

The same path with different velocity can express different intent.

### 6. Reality Compiler Integration

TrackGlyphKit can emit a human-input proof shard.

```text
intent → track glyph stream → command → artifact mutation → Layer4Meter receipt
```

This connects human gesture to artifact provenance.

## Receipt Format

```text
.trackglyph
├── manifest.json
├── gesture_stream.jsonl
├── dictionary.json
├── decoded_actions.jsonl
├── confidence.jsonl
├── shard_hashes.json
├── merkle_root.txt
└── report.md
```

### gesture_stream.jsonl

Each row:

```json
{
  "t": 0.128,
  "glyph": "◍◎⇄",
  "topology": "two_finger",
  "pressure_band": "deep",
  "trajectory": "horizontal_axis",
  "zone": "center",
  "velocity_band": "medium",
  "duration_ms": 96,
  "source": "app_local_trackpad_view"
}
```

### decoded_actions.jsonl

Each row:

```json
{
  "t0": 0.128,
  "t1": 0.384,
  "sequence": "◍◎⇄ ◌●━",
  "action": "zoom_then_inspect",
  "app_context": "RealityWallCanvas",
  "confidence": 0.87
}
```

## MVP Architecture

```text
TrackGlyphKit
├── TrackGlyphView
├── TouchFrameNormalizer
├── GestureFeatureExtractor
├── GlyphEncoder
├── SequenceParser
├── GlyphDictionary
├── ActionMapper
├── ReceiptWriter
└── DemoCanvas.app
```

### TrackGlyphView

An AppKit/SwiftUI-hosted view that receives gesture/touch/pressure events where public APIs allow.

### TouchFrameNormalizer

Normalizes:

- finger count
- phase
- location
- normalized zone
- pressure band
- velocity band
- duration

### GestureFeatureExtractor

Extracts:

- trajectory
- spread/pinch axis
- rotation direction
- acceleration
- rhythmic timing
- repeated pattern

### GlyphEncoder

Maps features to symbols.

### SequenceParser

Converts glyph streams into command sentences.

### GlyphDictionary

A JSON or YAML dictionary mapping glyph sequences to app commands.

### ActionMapper

Calls app actions only after confidence and safety policy pass.

### ReceiptWriter

Stores a privacy-safe gesture receipt.

## Demo App

Build:

```text
TrackGlyph Demo Canvas
```

Demo behaviors:

- draw glyph stream live
- show decoded action
- show confidence
- replay gesture sentence
- export `.trackglyph`
- map gestures to canvas operations

Example live HUD:

```text
Input:   ◌◉→ ◍◎⇄ ◌●━
Decode:  select → zoom → inspect
Confidence: 0.91
Receipt: sha256:...
```

## Apple Platform Reality

Apple’s public support docs show that Mac trackpads already support many Multi-Touch gestures: tap, swipe, pinch, spread, scroll, rotate, three-finger drag, Mission Control, App Exposé, and full-screen app switching. Force Touch trackpads can also support force click and haptic feedback.

Therefore the product should not claim that Apple trackpads are binary.

Correct statement:

> Apple trackpads already emit rich interaction. TrackGlyphKit preserves and encodes richer gesture structure before application logic collapses it into simple commands.

Incorrect statement:

> Trackpads are only binary 0/1 devices.

## Product Names

```text
TrackGlyphKit       = framework
TrackGlyph          = glyph stream format
GestureReceipt      = proof artifact
GlyphPad            = consumer/demo app
TouchGlyph          = alternate name
RealityPad          = Reality Compiler mode
```

## Integration With The Stack

```text
TrackGlyphKit   = gesture glyph encoder
OverLanguage    = command grammar target
Layer4Meter     = substrate receipt link
ReceiptOS       = proof ledger
Reality Compiler = artifact/value compiler
MirrorMind      = TV-safe presentation target
Reality Wall    = big-screen display target
```

## V1 Build Order

```text
1. AppKit demo view
2. basic gesture recognizers
3. pressure band if available
4. zone classifier
5. velocity/trajectory classifier
6. glyph encoder
7. sequence parser
8. dictionary-driven command mapper
9. visible HUD
10. `.trackglyph` receipt export
```

## Boundary Conditions

- V1 is app-local, not global.
- V1 should use public APIs only.
- V1 should not promise access to every raw trackpad sensor channel.
- V1 should not log sensitive gestures globally.
- Gesture receipts should be opt-in.
- Raw streams should be redacted or hashed where possible.
- Accessibility value must be tested with real users.
- Any claim of high state count must be calibrated empirically, not asserted from combinatorics alone.

## Final Law

```text
The binary pointer gives events.
TrackGlyph gives language.
```

Or:

```text
The trackpad stops being a mouse and becomes an instrument.
```
