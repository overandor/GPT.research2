# SensorGlyphKit: Multimodal Contact Glyphs

## Status

This document defines SensorGlyphKit, the next layer after TrackGlyphKit.

TrackGlyphKit turns trackpad contact into glyph language.

SensorGlyphKit fuses trackpad, microphone, and camera features into multimodal contact glyphs.

```text
trackpad = where + pressure + fingers + motion
microphone = contact sound + friction + tap force + rhythm
camera = finger pose + angle + hover + hand shape + intent context
```

Core primitive:

```text
finger movement
+ contact audio
+ camera hand pose
+ timing sync
= sensor-fused glyph
```

## Product Names

```text
TrackGlyphKit     = touch-only
SensorGlyphKit    = touch + mic + camera
FusionGlyph       = combined encoded event
ContactGlyph      = fused physical gesture signature
IntentReceipt     = proof object
TouchSpectra      = product/demo name for the sensory instrument
```

Best public name:

> **TouchSpectra**

Best developer framework name:

> **SensorGlyphKit**

## Thesis

Trackpad alone gives touch geometry.

Microphone gives contact texture.

Camera gives pre-contact posture and intent context.

Together:

```text
TactileGlyph + AudioGlyph + VisionGlyph + TimeGlyph = ContactGlyph
```

This turns a gesture from a local input event into a physical signature.

## Standards Grounding

W3C Pointer Events already treats pointer input as richer than mouse clicks. Pointer Events Level 3 includes pointer type, coordinates, pressure, contact geometry, tilt/angles, high-frequency `pointerrawupdate`, coalesced events, and predicted events.

SensorGlyphKit extends the same idea beyond pointer data into audio-visual-touch fusion.

Important: this is an architectural analogy. W3C Pointer Events does not define microphone or camera fusion.

## Apple API Direction

Use public Apple frameworks only:

```text
AppKit / NSTouch / NSEvent = app-local trackpad touch and gesture events
AVFoundation              = camera and microphone capture
Vision                    = hand pose / visual feature extraction where available
Core ML / MLX / local model = optional intent classifier
```

Do not rely on:

```text
private multitouch drivers
unsupported ANE access
hidden microphone recording
hidden camera recording
global spying
password inference
```

## What Microphone Adds

The microphone records the sound signature of contact.

Features:

```text
tap sharpness
fingerpad vs fingernail
scrape / glide friction
surface resonance
velocity proxy
rhythm
hesitation
force proxy
lift-off sound
micro-stutter
```

Examples:

```text
soft finger drag  = low friction hiss
nail scrape       = high-frequency scratch
force tap         = short impulse spike
hesitant movement = broken rhythm
confident flick   = clean transient
```

### Microphone Risk Boundary

This is privacy-sensitive.

Research has demonstrated acoustic side channels where microphones can infer sensitive input. The “Hearing your touch” paper showed that microphones on phones/tablets can recover information from tap sounds and infer tap locations. Keyboard acoustic side-channel research has also shown high classification accuracy from typing sounds.

Therefore:

```text
Use microphone only with explicit consent.
Never record hidden input.
Never infer passwords or PINs.
Never run globally.
Store features, not raw audio, unless the user explicitly exports encrypted raw data.
Show a visible recording indicator.
```

## What Camera Adds

The camera records pose and pre-contact geometry.

Features:

```text
finger angle
knuckle bend
hand approach direction
hover before contact
wrist posture
number of fingers before touch
left/right hand
two-hand gesture
off-trackpad context
hesitation before touch
```

This answers questions the trackpad cannot:

```text
Was the user about to touch?
Was the movement intentional?
Was it fingerpad, nail, knuckle, or side-of-finger?
Was the hand relaxed, tense, precise, or uncertain?
Was a palm drift being mistaken for a command?
```

## Fused Glyph Notation

Track-only glyph:

```text
◌◉→
```

Decoded:

```text
single finger press moving right
```

Sensor-fused glyph:

```text
◌◉→ · ʂ↑ · ∠low · τ220
```

Fields:

```text
TouchGlyph:   ◌◉→
SonicGlyph:   ʂ↑
VisionGlyph:  ∠low
TimeGlyph:    τ220
FusionGlyph:  ◌◉→·ʂ↑·∠low·τ220
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

## ContactGlyph Object

```json
{
  "kind": "ContactGlyph",
  "version": "0.1",
  "timestamp": "2026-06-27T12:00:00-04:00",
  "touch": {
    "glyph": "◌◉→",
    "zone": "center",
    "velocity": "medium",
    "pressure_tier": "press"
  },
  "audio": {
    "glyph": "ʂ↑",
    "features": ["friction_high", "clean_transient"],
    "raw_audio_stored": false
  },
  "vision": {
    "glyph": "∠low",
    "features": ["right_index", "low_angle", "stable_approach"],
    "raw_video_stored": false
  },
  "fusion": {
    "glyph": "◌◉→·ʂ↑·∠low·τ220",
    "intent": "precise_scrub_or_inspect",
    "confidence": 0.91
  }
}
```

## What This Unlocks

### 1. Intent Confidence

Same trackpad path, different meaning:

```text
quiet smooth drag + stable finger = deliberate move
scratchy drag + wobble + pause = uncertainty
hard tap + direct approach = confirm
soft tap + hover = preview
```

### 2. Better Accidental Input Rejection

Reject low-confidence commands when sensors disagree:

```text
trackpad says gesture
mic says no contact impulse
camera says palm drift
result: accidental / low confidence
```

### 3. Accessibility

Some users cannot perform precise gestures. Sensor fusion can accept alternate expressions:

```text
sound rhythm
pressure pulses
hand pose
hover timing
large-zone movement
```

The system can decode intent from multiple weak signals rather than requiring one perfect gesture.

### 4. Gesture Style Personalization

SensorGlyphKit can adapt to a user's style:

```text
soft operator
fast operator
hesitant operator
precise operator
expert operator
```

Boundary:

This is biometric-adjacent. Treat gesture style as private identity-sensitive data.

### 5. Intent Receipts

A stronger receipt can prove that the system observed a coordinated touch/audio/vision input event.

It should not claim to prove the user's inner mental state.

Correct claim:

```text
system observed fused contact expression matching inspect gesture with 0.91 confidence
```

Incorrect claim:

```text
user definitely intended to approve legally binding action
```

## `.contactglyph` Package

```text
.contactglyph
├── manifest.json
├── touch_stream.jsonl
├── audio_features.jsonl
├── vision_pose.jsonl
├── fused_glyphs.jsonl
├── decoded_intent.jsonl
├── confidence.jsonl
├── privacy_report.json
├── merkle_root.txt
└── report.md
```

Default storage:

```text
trackpad glyphs
audio features
vision features
fused glyphs
confidence
privacy report
hashes
```

Optional storage:

```text
encrypted raw audio/video, user-enabled only
```

Never store by default:

```text
raw microphone stream
raw camera stream
password/PIN inference
background sensor recording
```

## Architecture

```text
SensorGlyphKit
├── TrackpadStream
│   └── AppKit / NSTouch / NSEvent / gesture events
├── AudioContactStream
│   └── AVFoundation microphone capture / FFT / onset / friction / rhythm
├── VisionHandStream
│   └── camera / Vision hand pose / approach / finger identity hints
├── FusionClock
│   └── timestamp alignment
├── ContactGlyphEncoder
│   └── [touch | audio | vision | time] compound glyphs
├── IntentDecoder
│   └── command / macro / confidence
├── PrivacyGuard
│   └── consent / redaction / no raw defaults / visible sensor state
└── ReceiptExporter
    └── .contactglyph package
```

## Demo App: TouchSpectra

Live UI:

```text
left: trackpad heatmap + touch glyph
middle: audio spectrogram + sonic glyph
right: camera hand overlay + vision glyph
bottom: fused glyph sentence + decoded intent + confidence
```

MVP demo sequence:

1. opt into trackpad capture inside app view
2. opt into mic/camera separately
3. perform gesture
4. see touch/audio/vision glyphs
5. see fused ContactGlyph
6. export `.contactglyph` package
7. verify Merkle root

## Integration With Existing Stack

```text
TrackGlyphKit     = touch-only gesture language
SensorGlyphKit    = multimodal contact language
SonicGlyph        = audio proof / contact sound layer
VisionGlyph       = camera pose layer
Layer4Meter       = substrate + input receipt
MirrorMind        = TV-safe interpretation
Reality Wall      = proof display
ReceiptOS         = signed proof ledger
Reality Compiler  = packages workflow into value
```

## Product Boundary

System-wide SensorGlyphKit is dangerous.

App-local opt-in SensorGlyphKit is real.

Use this boundary:

```text
visible sensors
explicit permission
app-local capture
features-first storage
raw export only by user action
encrypted raw archives if needed
no password/PIN inference
no background microphone/camera capture
no claim of mind reading
```

## Final Law

```text
The trackpad feels contact.
The microphone hears contact.
The camera sees posture.
SensorGlyph compiles the three into expression.
```

Or:

```text
Trackpad gives the motion.
Microphone gives the texture.
Camera gives the posture.
FusionGlyph gives the confidence.
```
