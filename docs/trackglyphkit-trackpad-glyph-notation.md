# TrackGlyphKit: Trackpad Glyph Notation and Gesture-Receipt Layer

## Status

This document defines TrackGlyphKit: a Mac-native framework that treats the trackpad as a glyph emitter rather than a low-resolution event source.

It connects Apple's trackpad gesture model with the Reality Compiler stack:

```text
Trackpad microgesture → glyph stream → command grammar → app action → receipt
```

## Thesis

The binary pointer model gives applications events.

TrackGlyphKit gives applications gesture language.

Current interaction usually collapses trackpad behavior into a small set of recognized commands:

```text
tap
click
scroll
swipe
pinch / magnify
rotate
force click
```

TrackGlyphKit preserves more of the input shape:

```text
finger topology + phase + normalized position + motion + pressure + rhythm + zone
```

Then it compiles that shape into compound glyphs.

## Apple-Supported Grounding

Apple's archived Cocoa Event Handling Guide says OS X generates multitouch events, gesture events, and mouse events from MacBook trackpads; the hardware and operating system interpret common gestures, but applications can also receive and respond to gestures and multitouch events in distinctive ways.

Apple's archive also says raw touches are useful when OS X does not recognize the gesture you are interested in or when you want more information than AppKit's gesture event provides.

Important boundary:

- Prefer AppKit gesture events where they are enough.
- Use raw `NSTouch` events only inside an opted-in view.
- Do not rely on private multitouch driver APIs for V1.
- Do not make critical features available only through trackpad gestures, because users may not have a trackpad.

## Product Definition

TrackGlyphKit is a Swift/AppKit framework that:

1. captures supported trackpad gesture/touch input,
2. quantizes it into glyph tokens,
3. forms gesture sentences,
4. maps those sentences to commands,
5. records a gesture receipt.

It is not:

```text
a private driver hack
a replacement for accessibility input
a forced gesture-only UI
a binary click logger
```

## Core Primitive

```text
TouchFrame → GlyphAtom → GlyphPhrase → CommandIntent → ActionReceipt
```

Expanded:

```text
NSTouch / NSEvent
→ topology + phase + position + delta + pressure/rhythm if available
→ compound glyph
→ parser
→ command dictionary
→ app action
→ receipt hash
```

## Glyph Alphabet

### Topology

```text
◌  single finger
◍  two fingers
⬡  three fingers
⬢  four fingers
⬣  palm / resting / broad contact candidate
```

### Phase

```text
⊙  began
→  moved
⊚  stationary
⊘  ended
⊗  cancelled
```

### Pressure / Depth

Pressure availability depends on hardware/API surface. Treat this as optional and fallback-safe.

```text
·  hover / near-zero / no pressure
-  light touch
◉  press
◎  deep press
●  force click / maximum tier
```

### Motion

```text
→  right
←  left
↑  up
↓  down
↻  clockwise arc
↺  counter-clockwise arc
⇄  horizontal oscillation
⇅  vertical oscillation
∿  tremor / hesitation
⌁  flick / high velocity
⋯  drag / low velocity
```

### Spatial Zone

```text
⌖  center
◧  left edge
◨  right edge
◩  top
◪  bottom
⬔  corner
```

### Temporal / Rhythm

```text
⋅  tap / short duration
–  hold
━  long hold
⋯  continuous
♪  rhythmic pattern
```

## Compound Glyph Examples

### Force Inspect

```text
◌●━
```

Meaning:

```text
one finger + force/deep pressure + long hold = inspect / reveal more context
```

### Two-Finger Zoom

```text
◍◎⇄
```

Meaning:

```text
two fingers + deep pressure + contraction/expansion = zoom / semantic expand
```

### Three-Finger Flick Up

```text
⬡-↑⌁
```

Meaning:

```text
three fingers + light pressure + upward + high velocity = lift to overview / mission control style action
```

### Hesitant Motion

```text
◌-∿
```

Meaning:

```text
single light touch + tremor / hesitation = show help / preview / do not execute yet
```

## Trackpad As Language

Events say:

```text
user clicked
```

Glyph phrases say:

```text
user expressed ◌◉→ ◍◎⇄ ⬡-↻
```

Which can decode as:

```text
select → zoom/expand → rotate/orient
```

This creates a gesture sentence rather than a single event.

## What This Unlocks

### 1. Glyph Command Language

Applications can register command dictionaries:

```text
◌◉→  = select mode
◍◎⇄  = zoom / expand
⬡-↻  = rotate / orient
◌●♪  = command palette
```

### 2. Pressure-Graded Fidelity Ladder

A single gesture can disclose more based on depth:

```text
L0 ·◌  preview only
L1 -◌  select
L2 ◉◌  activate
L3 ◎◌  inspect / expand
L4 ●◌  full context / command menu
```

### 3. Chord Input

Multiple fingers and zones can act like piano chords:

```text
◧◌◉ + ◨◍- = split / compare view
⬔◌● + ⬔◍● = screenshot / region capture intent
```

### 4. Temporal Macros

A glyph stream can be recorded, named, replayed, and shared:

```text
◌◉→  ◍◎⇄  ⬡-↻
```

Possible uses:

- macro recording
- gesture recipes
- app-specific command packs
- replayable tutorial gestures
- undo/reverse interpretation

### 5. Intent Confidence

Velocity and hesitation can produce soft intent signals:

```text
⌁ = execute / throw / dismiss
⋯ = place / slowly arrange
∿ = uncertain / show help
```

### 6. Layer4Meter Input Receipts

TrackGlyphKit can emit input receipts:

```text
SESSION: 2026-06-27T11:04:22-04:00
STREAM: ◌-→ ◌-→ ◍◎⇄ ◌●━ ⬡-↻
DECODED: scroll, zoom, inspect, orient
HASH: sha256:...
```

This proves user intent at the input layer without storing sensitive screen contents.

## V1 Architecture

```text
TrackGlyphKit
├── AppKit touch/gesture listener
├── touch frame normalizer
├── zone classifier
├── topology classifier
├── velocity/rhythm classifier
├── optional pressure tier classifier
├── glyph encoder
├── phrase parser
├── command dictionary
├── receipt writer
└── demo visualizer
```

## V1 Apple API Strategy

Use supported AppKit surfaces:

- `magnifyWithEvent:` for magnification/pinch where AppKit provides it.
- `rotateWithEvent:` for rotation.
- `swipeWithEvent:` for swipe.
- scroll wheel events for scrolling and momentum phases.
- `touchesBeganWithEvent:`, `touchesMovedWithEvent:`, `touchesEndedWithEvent:`, `touchesCancelledWithEvent:` for raw touch sequences inside an opted-in custom view.
- `NSTouch.identity` for tracking a finger through a sequence.
- `NSTouch.normalizedPosition` and `NSTouch.deviceSize` for trackpad-local coordinates.

V1 should not require:

- private `MultitouchSupport.framework`
- kernel extensions
- global private touch spying
- unsupported pressure APIs
- gestures as the only path to a critical command

## Integration With Reality Compiler

```text
TrackGlyphKit     = human gesture encoding layer
OverLanguage      = command grammar
Layer4Meter       = input/substrate receipt
ReceiptOS         = signed proof ledger
MirrorMind        = TV-safe screen interpretation
Reality Wall      = proof display
Reality Compiler  = packages the whole workflow into value
```

## Product Names

```text
TrackGlyphKit   = framework name
TrackGlyph      = notation / stream format
GestureReceipt  = output proof object
GlyphPad        = consumer/demo app
```

## Demo App: GlyphPad

A small Swift app that shows:

```text
left pane: live trackpad glyph stream
center: decoded gesture phrase
right pane: command intent + receipt hash
```

MVP demo modes:

1. Draw glyph stream.
2. Trigger command phrase.
3. Record gesture macro.
4. Export gesture receipt.
5. Replay gesture phrase visually.

## Boundary Conditions

TrackGlyphKit must avoid overclaiming.

- It does not expose every possible hardware microstate.
- It does not bypass macOS privacy/security.
- It does not replace keyboard/mouse accessibility paths.
- It should not rely on private driver APIs in V1.
- Pressure/depth tiers must degrade gracefully if unavailable.
- App-specific command dictionaries must be explicit and user-editable.
- Gesture receipts prove an observed input stream, not the user's internal intention.

## Final Law

```text
The pointer gives coordinates.
The trackpad gives gestures.
TrackGlyph gives gestures grammar.
```

Or:

```text
Clicking is input.
Glyphing is expression.
```
