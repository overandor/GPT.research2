# SensorGlyphKit: Multimodal Fusion Glyphs and Intent Receipts

## Status

This document defines **SensorGlyphKit**, the multimodal expansion of TrackGlyphKit.

TrackGlyphKit captures touch geometry.

SensorGlyphKit fuses:

```text
trackpad touch + microphone features + camera pose + timing sync
```

into:

```text
FusionGlyph + IntentReceipt
```

## Product Definition

SensorGlyphKit is a Mac-native, app-local, opt-in framework that encodes multimodal human input as privacy-preserving glyph streams.

It does not secretly watch or listen.

It exists to turn visible/consented interaction into structured intent evidence.

## Core Primitive

```text
finger movement
+ contact audio
+ camera hand pose
+ timing sync
= sensor-fused glyph
```

Expanded:

```text
TouchGlyph + SonicGlyph + VisionGlyph + TimeGlyph → FusionGlyph → IntentReceipt
```

## Why Trackpad Alone Is Not Enough

Trackpad alone gives:

```text
where + fingers + motion + phase + optional pressure
```

Microphone adds:

```text
contact sound + friction + tap force proxy + rhythm
```

Camera adds:

```text
finger pose + hand angle + hover + hand shape + off-trackpad context
```

Together:

```text
motion + texture + posture + timing = stronger intent signal
```

## Technical Grounding

W3C Pointer Events Level 3 shows the general direction: pointer input is not just a mouse click. It includes hardware-agnostic pointer events for mouse, pen, and touch; properties such as pressure, contact geometry, and tilt; high-frequency `pointerrawupdate`; coalesced events; and predicted events.

SensorGlyphKit extends that principle beyond pointer streams into local multimodal sensor fusion.

Important boundary:

```text
Pointer Events = standardized pointer input model.
SensorGlyphKit = local application framework for fusing touch, audio, vision, and time into app-specific intent receipts.
```

## What The Microphone Adds

The microphone can contribute acoustic features:

```text
tap sharpness
fingerpad vs fingernail clue
scrape / glide friction
surface resonance
velocity proxy
rhythm
hesitation
force proxy
```

Examples:

```text
soft finger drag  = low friction hiss
nail scrape       = high-frequency scratch
force tap         = short impulse spike
hesitant movement = broken rhythm
confident flick   = clean transient
```

### Microphone Privacy Boundary

Microphone input is dangerous because acoustic input can leak sensitive information.

Research has shown touch sounds can form side channels. “Hearing your touch” demonstrated that microphones can capture touch-generated sound waves and use their distortions to infer tap locations on phones/tablets. Keyboard acoustic side-channel research has also shown high classification accuracy from typing sounds.

Therefore SensorGlyphKit must obey:

```text
Use microphone only with explicit consent.
Never record hidden input.
Never infer passwords, PINs, or typed secrets.
Never run globally.
Never run in the background without a visible recording indicator/UI.
Store extracted features, not raw audio, unless the user explicitly exports raw evidence.
Disable audio fusion automatically near password/secure-input fields where detectable.
```

## What The Camera Adds

The camera can contribute pose and pre-contact geometry:

```text
finger angle
knuckle bend
hand approach direction
hover before contact
wrist posture
number of fingers before touch
left/right hand
hesitation before touch
off-trackpad context
```

This helps answer:

```text
Was the user about to touch?
Was the movement intentional?
Was it fingerpad, nail, knuckle, or side of finger?
Was it relaxed, hesitant, precise, or forceful?
```

### Camera Privacy Boundary

Camera input is biometric and context-sensitive.

SensorGlyphKit must obey:

```text
Use camera only with explicit consent.
Show visible active-camera state.
Prefer hand-pose features over raw video storage.
Do not identify faces or bystanders.
Do not run globally.
Do not classify identity unless the user explicitly enables a separate personalization feature.
Do not store raw frames unless user exports an evidence packet.
```

## Apple API Direction

Use public Apple surfaces only:

```text
AppKit / NSTouch / NSEvent     = touch and gesture input inside opted-in views
AVFoundation                   = camera/microphone capture pipeline
Vision                         = visual analysis / hand-pose style processing where supported
ScreenCaptureKit               = optional screen context in MirrorMind/Reality Wall workflows
Core ML / MLX / local model    = optional local inference
```

Do not use:

```text
private multitouch drivers
hidden microphone capture
hidden camera capture
kernel extensions
unsupported ANE pathways
raw biometric profiling by default
```

## FusionGlyph Notation

Instead of a touch-only glyph:

```text
◌◉→
```

Meaning:

```text
single finger press moving right
```

SensorGlyphKit emits:

```text
◌◉→·ʂ↑·∠low·τ220
```

Where:

```text
TouchGlyph:   ◌◉→      single-finger pressure drag
SonicGlyph:   ʂ↑        high-friction / sharp scrape feature
VisionGlyph:  ∠low      low finger angle / deliberate contact posture
TimeGlyph:    τ220      220ms duration
FusionGlyph:  combined event
```

Decoded:

```text
single-finger pressure drag
with high-friction scrape
low finger angle
short deliberate duration
intent: precise scrub / inspect
confidence: 0.91
```

## What This Unlocks

### 1. Intent Confidence

Same trackpad path, different fused meaning:

```text
quiet smooth drag + stable finger posture = deliberate move
scratchy drag + wobble + pause           = uncertainty
hard tap + direct approach                = confirm
soft tap + hover                          = preview
```

### 2. Multimodal Accessibility

Users who cannot perform precise gestures can express intent through multiple weak signals:

```text
sound rhythm
pressure pulses
hand pose
hover timing
large-zone movement
```

### 3. Gesture Personalization

A user can optionally train personal gesture style:

```text
rhythm
pressure curve
scrape profile
approach angle
hand posture
```

Boundary:

```text
Treat personalization as sensitive biometric-style data.
Keep it local by default.
Make delete/export controls obvious.
```

### 4. Stronger Intent Receipts

A gesture receipt can contain:

```text
.sensorglyph
├── manifest.json
├── touch_stream.jsonl
├── audio_features.jsonl
├── vision_pose.jsonl
├── fused_glyphs.jsonl
├── decoded_intent.jsonl
├── confidence.jsonl
├── privacy_policy.json
├── shard_hashes.json
└── merkle_root.txt
```

This changes a receipt from:

```text
user clicked
```

to:

```text
user expressed intent through touch + sound + pose under consented capture policy
```

## V1 Architecture

```text
SensorGlyphKit
├── TrackGlyphKit touch stream
├── microphone feature extractor
├── camera pose extractor
├── timestamp synchronizer
├── fusion window builder
├── FusionGlyph encoder
├── intent confidence scorer
├── privacy policy gate
├── receipt writer
└── demo visualizer
```

## V1 Feature Extraction

### Touch Features

```text
finger count
touch phase
normalized position
velocity
direction
zone
rhythm
pressure tier if available
```

### Audio Features

```text
short-time energy
spectral centroid
onset strength
impulse duration
friction band energy
rhythm interval
```

Store only derived features by default.

### Vision Features

```text
hand present / absent
finger count candidate
approach vector
hand bounding box
finger angle candidate
hover timing
confidence
```

Store only pose/keypoint/feature summaries by default.

### Timing Features

```text
event timestamp
modality latency
fusion window id
start / end time
inter-event interval
```

## Fusion Window

Use short windows to combine modalities:

```text
window_size = 50ms to 250ms
```

Example:

```text
Touch event at t0
Audio transient at t0 + 12ms
Camera pose at t0 - 33ms
→ one FusionGlyph
```

## Integration With The Stack

```text
TrackGlyphKit     = touch-only gesture grammar
SensorGlyphKit    = multimodal gesture grammar
SonicGlyph        = audio feature layer
VisionGlyph       = camera/pose feature layer
Layer4Meter       = receipt and substrate accounting
MirrorMind        = privacy-safe presentation and screen-risk checks
Reality Wall      = proof display
Reality Compiler  = packages intent, work, proof, and value
```

## Product Names

```text
TrackGlyphKit   = touch-only framework
SensorGlyphKit  = touch + mic + camera framework
FusionGlyph     = combined encoded event
IntentReceipt   = proof object
GlyphPad        = touch demo app
SensorPad       = multimodal demo app
```

## Demo App: SensorPad

A small Mac app that shows:

```text
left: live touch glyph stream
middle: audio/vision feature meters
right: fused glyph + decoded intent + confidence
bottom: privacy mode + receipt hash
```

MVP demo modes:

1. Touch-only.
2. Touch + audio.
3. Touch + camera pose.
4. Full fusion.
5. Export IntentReceipt.

## Safety / Abuse Rules

SensorGlyphKit must refuse or disable:

```text
password inference
PIN inference
keystroke inference
background microphone spying
background camera spying
hidden biometric profiling
silent sensor capture
bystander identification
raw sensor upload by default
```

The system should label these attempts as:

```text
unsupported / unsafe / outside product boundary
```

## Final Law

```text
Trackpad gives the motion.
Microphone gives the texture.
Camera gives the posture.
FusionGlyph gives the intent.
```

Boundary law:

```text
No hidden sensors.
No secret inference.
Consent first, features first, raw data last.
```
