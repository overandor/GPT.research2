# MirrorMind: AirPlay LLM Doctor and TV-Safe Mirror Assistant

## Status

This document defines the product spec for a supportable Mac app that diagnoses AirPlay issues, prevents accidental private-screen leakage, and turns messy desktop state into TV-safe output.

Working names:

```text
MirrorMind       = best consumer name
AirPlay Doctor   = best utility name
Reality Wall Mode = best pro/demo mode
```

Recommended product name:

> **MirrorMind**

## Product Definition

MirrorMind is a local Mac app that:

1. diagnoses AirPlay failure,
2. guides the user through Apple-supported AirPlay paths,
3. protects private screen-sharing,
4. converts desktop state into TV-safe presentation cards,
5. optionally uses a local LLM to explain risks and fixes.

It is not:

```text
an AirPlay clone
a protocol hack
a generic casting app
a fake screen mirror
a reverse-engineered AirPlay implementation
```

## Core Rule

Do not reverse-engineer AirPlay.

AirPlay moves pixels.

MirrorMind understands the screen, the room, and the risk.

## Official Surface

Apple exposes the supported path for Mac-to-TV AirPlay:

```text
Control Center → Screen Mirroring → select TV → enter code if asked → choose share window, mirror, or extend
```

Apple also says both devices should have Wi-Fi turned on and be on the same network before using AirPlay.

MirrorMind should guide this path instead of replacing it.

## Product Wedge

The killer wedge is:

> **TV-Safe Mode**

Before the user mirrors to a TV, MirrorMind checks whether the user is about to expose:

- Gmail
- Messages
- terminal secrets
- browser tabs
- private filenames
- Downloads folder
- client names
- tokens / API keys
- calendars
- medical / legal / financial documents

Then it recommends:

```text
window-only share
mirror entire screen
extend display
cancel mirroring
use HDMI fallback
open Reality Wall Mode
```

## MVP Architecture

```text
MirrorMind.app
SwiftUI menu-bar app
│
├── AirPlay Readiness Checker
│   ├── Wi-Fi on/off
│   ├── same-network check
│   ├── VPN active?
│   ├── firewall state
│   ├── receiver visible?
│   ├── passcode expected?
│   └── HDMI fallback recommendation
│
├── TV-Safe Mode
│   ├── ScreenCaptureKit snapshot
│   ├── window/title inventory
│   ├── secret-risk scanner
│   ├── privacy warnings
│   └── recommended share mode
│
├── Local LLM Engine
│   ├── MLX / llama.cpp / Ollama
│   ├── no cloud upload by default
│   └── explainable fix checklist
│
├── Presentation Transformer
│   ├── big TV cards
│   ├── private fields hidden
│   ├── QR handoff
│   └── Reality Wall mode
│
└── Receipt Logger
    ├── what was shown
    ├── what was hidden
    ├── timestamp
    └── hash receipt
```

## Feature Set V1

1. Diagnose AirPlay.
2. Explain why TV does not appear.
3. Explain why TV appears but fails.
4. Detect VPN / network / firewall likely blockers.
5. Give exact Apple-supported fix steps.
6. Recommend window-only vs mirror vs extend.
7. Scan visible desktop privacy risks.
8. Build TV-safe presentation cards.
9. Log a shown/not-shown receipt.
10. Offer HDMI / Reality Wall fallback.

## Example Demo

User clicks:

```text
MirrorMind → Prepare TV
```

App says:

```text
Samsung TV detected.
AirPlay visible but unstable.
VPN active: likely discovery problem.
Recommended fix: disable VPN for local network discovery.
Safe share mode: Window only.
Privacy risk: Messages and Gmail visible.
Presentation ready: 6 TV-safe cards.
```

Then the app opens or points the user to:

```text
Control Center → Screen Mirroring
```

## Local LLM Role

The LLM should not be the AirPlay mechanism.

The LLM should:

- explain probable causes
- rank safe fix steps
- summarize visible-window risks
- convert desktop chaos into presentation cards
- produce a privacy checklist
- generate a receipt summary

Default local engines:

```text
MLX        = Apple Silicon optimized path
llama.cpp  = lightweight local runtime path
Ollama     = easiest local developer/user path
Core ML    = Apple-supported deployment framework for model packages
```

## macOS Capture / Media Anchors

Use Apple-supported frameworks:

```text
ScreenCaptureKit = snapshot/window/display inspection
VideoToolbox     = hardware encode/decode when video paths are needed
SwiftUI/AppKit   = Mac UI
Network.framework / system APIs = diagnostics where applicable
```

MirrorMind should not depend on unsupported ANE access or private AirPlay internals.

## Privacy Policy By Design

Default:

```text
no cloud upload
no full screen recording by default
no token logging
no raw screenshot storage unless user opts in
hash/redact risky evidence
store only receipt summaries where possible
```

TV-Safe Mode should prefer:

```text
window inventory
risk labels
redacted thumbnails
hashes
presentation cards
```

over raw full-desktop recordings.

## Reality Wall Mode

Reality Wall Mode is the professional/demo layer.

It transforms desktop state into:

- proof cards
- file cards
- receipt cards
- artifact timeline
- demo agenda
- QR handoff
- safe client presentation view

This turns AirPlay from:

```text
mirror everything
```

into:

```text
show only what is safe and useful
```

## Use Cases

### Consumer

```text
Why is my TV not showing up?
Why does AirPlay connect then fail?
What should I share without exposing private stuff?
```

### Professional

```text
Prepare client presentation.
Show only selected proof cards.
Hide messages, terminal, files, and private tabs.
Create a shown/not-shown receipt.
```

### Reality Compiler

```text
Show Layer4Meter receipts.
Show JORKI file sessions.
Show LambdaReceipt buyer packets.
Show SonicGlyph audio/video proof.
```

## Public Promise

> Before you mirror, know what you’re showing.

## Buyer Line

> MirrorMind fixes AirPlay confusion and prevents accidental TV-screen leaks.

## Pro Line

> Turn your Mac into a private, local LLM-powered presentation brain for any room.

## MVP Build Order

```text
1. SwiftUI menu-bar shell
2. AirPlay checklist UI
3. Wi-Fi / VPN / firewall diagnostic hints
4. manual receiver checklist
5. ScreenCaptureKit snapshot permission
6. window/title inventory
7. secret-risk scanner
8. local LLM explanation layer
9. TV-safe card builder
10. shown/not-shown receipt export
```

## Avoid

Do not build:

- AirPlay reverse-engineering
- DLNA caster as the core product
- full screen recorder first
- cloud screenshot upload
- local TV inference requirement
- unsupported ANE pathway
- spyware-like monitoring

## Final Law

```text
AirPlay is the cable.
MirrorMind is the intelligence before the mirror.
```

Or:

```text
AirPlay moves pixels.
MirrorMind protects meaning.
```
