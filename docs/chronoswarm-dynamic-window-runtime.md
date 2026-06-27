# ChronoSwarm: Dynamic Window Runtime for Future-Scheduled Work

## Status

This document defines the primitive described as:

```text
genetic window resizing
+ quadrant screen database
+ scheduled process awakening
+ trackpad-as-screen input surface
= future-scheduled screen operating system
```

The product name is:

> **ChronoSwarm**

The underlying runtime name is:

> **ChronoQuadrantOS**

## Thesis

A screen should not be a static canvas.

A screen should be a living work allocator.

Instead of the user manually resizing windows, opening tools, and deciding what to look at, the system should:

1. observe the screen as queryable state,
2. divide the workspace into active quadrants,
3. assign each quadrant a role,
4. resize and rearrange windows based on workload pressure,
5. awaken scheduled workflows before they are manually requested,
6. remove or collapse windows when their job is complete,
7. record receipts for every layout, process, and action.

## Core Law

```text
The user should not arrange windows.
The runtime should arrange attention.
```

## Existing Foundation

The current macOS screen-as-database work already proved the direction:

```text
screen → windows/processes/UI elements → SQLite rows → SQL queries → control actions
```

ChronoSwarm adds the missing layer:

```text
SQL-observed screen state
+ genetic layout policy
+ timed workflow planner
+ quadrant agents
+ trackpad-screen input
= self-adjusting work surface
```

## Architecture

```text
ChronoSwarm
├── ScreenDB
│   ├── windows table
│   ├── processes table
│   ├── screenshots table
│   ├── ui_elements table
│   ├── trackpad_events table
│   └── actions table
│
├── QuadrantRuntime
│   ├── Q0 research / observe
│   ├── Q1 build / execute
│   ├── Q2 verify / audit
│   └── Q3 dashboard / receipt
│
├── GeneticLayoutGovernor
│   ├── layout genome
│   ├── fitness function
│   ├── mutation
│   ├── crossover
│   ├── selection
│   └── rollback
│
├── ChronoScheduler
│   ├── time-of-day workflows
│   ├── file-change triggers
│   ├── idle triggers
│   ├── deadline triggers
│   └── launchd/user-agent bridge
│
├── WindowActuator
│   ├── move window
│   ├── resize window
│   ├── focus window
│   ├── hide / unhide
│   ├── tile / split
│   └── restore prior layout
│
├── TrackpadScreen
│   ├── trackpad-sized overlay
│   ├── thermal pressure map
│   ├── gesture database
│   ├── quadrant routing
│   └── remote operator input
│
└── ReceiptOS
    ├── layout receipts
    ├── action receipts
    ├── screenshot receipts
    ├── process receipts
    └── schedule receipts
```

## ScreenDB Tables

```sql
windows(id, app, title, x, y, w, h, z, focused, quadrant, role, timestamp)
processes(pid, name, cpu, memory, started_at, role, quadrant)
screenshots(id, quadrant, path, sha256, timestamp)
ui_elements(id, window_id, role, label, x, y, w, h, confidence)
trackpad_events(id, operator_id, x, y, pressure, gesture, glyph, timestamp)
actions(id, type, target, args_json, result, receipt_hash, timestamp)
schedules(id, workflow, trigger, next_run, last_run, status)
layouts(id, genome, fitness, score, applied_at, reverted_at)
```

## Genetic Layout Genome

A layout genome is a compact description of the current workspace:

```json
{
  "quadrants": {
    "Q0": {"role": "research", "rect": [0, 0, 0.50, 0.50], "priority": 0.8},
    "Q1": {"role": "builder", "rect": [0.50, 0, 0.50, 0.50], "priority": 1.0},
    "Q2": {"role": "verifier", "rect": [0, 0.50, 0.50, 0.50], "priority": 0.7},
    "Q3": {"role": "receipt", "rect": [0.50, 0.50, 0.50, 0.50], "priority": 0.6}
  },
  "focus": "Q1",
  "density": 0.73,
  "mutation_rate": 0.08
}
```

## Fitness Function

```text
LayoutFitness =
  α·active_task_visibility
+ β·error_visibility
+ γ·stdout_readability
+ δ·receipt_visibility
+ ε·human_focus_score
+ ζ·agent_progress_score
- η·occlusion_penalty
- θ·context_switch_penalty
- ι·privacy_leak_penalty
- κ·screen_noise_penalty
```

The genome with the best score controls the next window layout.

## Genetic Operations

```text
mutation:
  expand active quadrant
  shrink idle quadrant
  swap research/build quadrants
  split one browser into two panes
  collapse completed workflow
  promote failing verifier to center

crossover:
  combine morning layout with current task pressure
  combine user manual preference with agent telemetry
  combine deadline layout with proof-wall layout

selection:
  keep layout if task throughput improves
  rollback if user cancels, error rises, or privacy risk increases
```

## ChronoScheduler

The scheduler plants workflows into the future.

A workflow may awaken because of:

```text
clock time
calendar window
file changed
build failed
idle machine
new email/message/API event
deadline approaching
previous workflow completed
LLM predicted preparation need
```

Example:

```json
{
  "workflow": "daily_proof_packet",
  "trigger": "08:30 weekdays",
  "prewarm": "08:20",
  "quadrant": "Q3",
  "actions": [
    "open receipts",
    "run verifier",
    "summarize overnight deltas",
    "show proof wall",
    "collapse when complete"
  ]
}
```

## Supported macOS Grounding

### Observation

Use public/permissioned surfaces first:

```text
CGWindowList / window metadata
ScreenCaptureKit / screenshots and window capture
Accessibility API / UI element tree where permissioned
process table / ps / NSWorkspace
FSEvents / file changes
unified log / trackpad event metadata where available
```

### Control

Use public/permissioned control surfaces first:

```text
AXUIElement window position and size attributes
NSWorkspace app activation
AppleScript/System Events only as optional adapter
Process / structured commands for owned tools
launchd user agents for scheduled background wakeups
```

Never rely on private APIs as the default path.

Never bypass macOS permission prompts.

## Trackpad As Screen

The trackpad becomes a physical mini-screen.

```text
trackpad surface = input map
overlay window   = visual map
heat map         = pressure / frequency / attention
quadrants        = work partitions
remote operator  = synthetic trackpad channel with permission
```

The overlay should be exactly trackpad-shaped.

When the user presses a region, that region warms visually:

```text
cold   = idle
warm   = active
hot    = pressure / repeated use
white  = command confirmed
red    = blocked / dangerous
```

This creates a structural separation between:

```text
where the user touches
what quadrant receives the gesture
what workflow awakens
what receipt is written
```

## Remote Trackpad Outsourcing

Remote input is allowed only as explicit collaboration.

Rules:

```text
visible remote operator label
session consent
operator role scope
quadrant scope
no background control
all remote gestures logged
panic pause button
per-operator receipt
```

A remote operator is not a hidden mouse.

It is a named input stream.

## Window Awakening Model

A window may be:

```text
sleeping  = hidden/collapsed but scheduled
warming   = preloaded but not focused
awake     = visible and active
working   = running process/tool
cooling   = finishing and summarizing
archived  = receipt written and hidden
```

This turns a program into a timed organism.

## Example One-Hour Dense Workflow

```text
00:00  Q0 opens research corpus
00:02  Q1 opens Builder workspace
00:05  Q2 opens Verifier logs
00:10  GeneticLayout expands Q1 because build is active
00:15  Q0 collapses, Q2 expands because tests failed
00:20  Q3 wakes ReceiptOS, displays proof chain
00:30  Q1 shrinks, browser split into prompt + docs
00:45  Q2 runs final verifier
00:55  Q3 exports packet
01:00  all nonessential windows archive themselves
```

## What Makes It Different From Normal Tiling

Normal tiling:

```text
human arranges windows
```

ChronoSwarm:

```text
runtime predicts attention demand
runtime mutates layout
runtime schedules work
runtime controls windows
runtime writes receipts
```

## Safety Boundary

ChronoSwarm must not become spyware or chaos automation.

Rules:

- visible control mode
- explicit accessibility and screen permissions
- per-workspace scope
- panic pause
- manual override always wins
- receipt every action
- rollback previous layout
- no secret capture by default
- no remote input without visible consent
- no uncontrolled shell execution

## MVP Build Order

1. ScreenDB snapshot: windows, apps, processes, screenshots.
2. SQL query UI.
3. Manual quadrant assigner.
4. WindowActuator: move/resize/focus only.
5. Receipt every layout change.
6. Simple layout fitness score.
7. Genetic mutation over quadrant sizes.
8. ChronoScheduler with one timed workflow.
9. TrackpadScreen overlay heatmap.
10. Remote operator input with consent.
11. Future workflow queue.
12. Integration with Builder cursor.

## Acceptance Test

```text
Given two browser windows and one terminal,
When Builder is running tests,
Then ChronoSwarm expands Builder quadrant,
shrinks idle research quadrant,
captures before/after screenshots,
writes a layout receipt,
and restores the prior layout on command.
```

## Final Law

```text
The screen is not a desktop.
The screen is a scheduled runtime.
```

Or:

```text
Do not manage windows.
Breed layouts.
Do not open apps.
Awaken workflows.
```
