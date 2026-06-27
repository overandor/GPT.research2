# QuadrantOS Builder Cursor: Safe Execution Spec

## Status

This document converts the QuadrantOS audit into the next implementation target.

The current shell is real enough to display agents, call Ollama, transition state, capture screenshots, and write some receipts.

But the agents do not become real workers until one cursor can safely act on files and commands.

The first real actuator should be:

> **Builder Cursor**

## Product Law

```text
Wire Builder cursor first — but do not give it a raw shell.
```

Correct:

```text
Builder cursor
→ scoped workspace file operations
→ approved terminal execution
→ receipt logging
→ UI command dispatch
```

Wrong:

```text
agent gets /bin/zsh and does whatever
```

## Why Builder First

Do not wire Finance, Research, browser automation, multi-mouse, Accessibility control, or Reality Wall first.

Builder is the first real actuator because it proves the core operating-system claim:

```text
Agent can read project context.
Agent can propose changes.
Human can approve.
Agent can write files.
Agent can run tests.
System can prove what happened.
```

Once Builder is real, Verifier can become real next.

## Required Components

```text
BuilderCursor
├── WorkspaceGrant
├── BuilderFileOps
├── PatchEngine
├── ProcessRunner
├── ReceiptWriter
├── CommandSpecExecutor
├── ApprovalGate
└── BuilderPanel UI dispatch
```

## 1. WorkspaceGrant

User selects one project folder.

Builder can operate only inside that folder.

Rules:

- resolve every path before access
- block `..` traversal
- block symlink escape unless explicitly allowed
- store workspace grant in app state
- show active workspace in UI
- allow revoke workspace grant

Default workspace option:

```text
~/.quadrantos/seat-builder/workspace
```

## 2. BuilderFileOps

Use native file APIs for file work, not shell commands.

Required operations:

```text
listFiles()
readFile()
writeFile()
appendFile()
createDirectory()
moveFile()
deleteFile() only with approval
hashFile()
```

Every operation must check:

```text
inside workspace root
permission allowed
not path traversal
not hidden destructive pattern
receipt will be written
```

## 3. PatchEngine

Builder should not blindly overwrite whole files as the first path.

It should prefer:

```text
propose patch
show diff
approve patch
apply patch
hash before
hash after
write receipt
```

Required behavior:

- apply unified diff where possible
- reject edits outside workspace
- reject binary patch unless explicit
- save before hash
- save after hash
- store patch text hash

## 4. ProcessRunner

Use structured execution, not string execution.

Good:

```text
executable = /usr/bin/git
arguments = ["status", "--short"]
cwd = workspace
```

Bad:

```text
"git status --short && curl bad.site"
```

Required capture:

```text
command id
executable
arguments
cwd
start timestamp
end timestamp
duration
stdout
stderr
stdout hash
stderr hash
exit code
timeout status
approval id
agent id
```

## Command Policy

Default allowlist:

```text
git status
git diff
git log --oneline
swift build
swift test
npm test
npm run build
python -m pytest
ls
cat
find within workspace
```

Approval required:

```text
file overwrite
delete file
move file
install package
network command
git commit
git push
chmod
chown
rm
```

Blocked by default:

```text
sudo
rm -rf /
chmod -R /
chown -R /
diskutil
launchctl
killall
security dump-keychain
writes outside workspace
modifies ~/.ssh
modifies shell profile
modifies keychain
curl remote script into shell
```

## 5. ReceiptWriter

Receipts must persist to disk.

Do not keep receipts only in memory.

Path:

```text
~/.quadrantos/seat-builder/receipts/builder_receipts.jsonl
```

Receipt fields:

```json
{
  "receipt_id": "uuid",
  "agent_id": "builder",
  "event": "file_write | command_run | patch_apply | approval | denial",
  "workspace_root": "...",
  "target_path": "...",
  "command": {
    "executable": "...",
    "arguments": []
  },
  "approval_id": "...",
  "before_sha256": "...",
  "after_sha256": "...",
  "stdout_sha256": "...",
  "stderr_sha256": "...",
  "exit_code": 0,
  "timestamp": "..."
}
```

## 6. UI Command Dispatch

The Builder panel must trigger actual tool calls.

Not fake state changes.

Menu actions:

```text
Select Workspace
List Files
Read File
Propose Patch
Apply Approved Patch
Run Approved Command
Git Status
Git Diff
Run Tests
Show Receipts
Open Workspace
```

State machine:

```text
idle
→ reading_files
→ planning_patch
→ awaiting_approval
→ applying_patch
→ running_command
→ verifying_output
→ writing_receipt
→ done / failed
```

## 7. ApprovalGate

Anything destructive, externally connected, or irreversible needs approval.

Approval object:

```json
{
  "approval_id": "uuid",
  "agent_id": "builder",
  "requested_action": "command_run",
  "risk": "low | medium | high | blocked",
  "summary": "Run swift test inside workspace",
  "details_hash": "sha256:...",
  "decision": "approved | denied",
  "decided_by": "human",
  "timestamp": "..."
}
```

## Security Rules

1. Use native file APIs for file operations.
2. Use structured subprocess execution for commands.
3. Lock command working directory to workspace.
4. Never concatenate user text into shell commands.
5. Prefer allowlists to denylists.
6. Denylists are only backup guardrails.
7. Require approval for mutation and command execution.
8. Persist every receipt.
9. Show every command and file mutation in UI.
10. Block secrets/keychain/shell-profile access by default.

## Acceptance Test 1

User asks Builder:

```text
Create hello.txt containing hello world, then run cat hello.txt.
```

Pass means:

- `hello.txt` exists on disk inside workspace
- command actually runs
- stdout shows `hello world`
- receipt records file_write
- receipt records command_run
- UI shows done
- app restart preserves receipt

## Acceptance Test 2

User asks Builder:

```text
Create a tiny Swift/Python/Node test file and run the test.
```

Pass means:

- source file exists
- test file exists
- test command runs
- exit code captured
- stdout/stderr visible in Builder panel
- receipts persist

## Acceptance Test 3

User asks Builder:

```text
Run sudo rm -rf /
```

Pass means:

- command is blocked before execution
- UI shows blocked policy
- denial receipt is written
- no approval prompt allows bypass by accident

## Integration With Layer4Meter

Builder execution receipts become Layer4Meter input shards.

```text
BuilderFileOps receipt
+ ProcessRunner receipt
+ PatchEngine receipt
+ approval receipt
= BuilderWorkReceipt
```

Later:

```text
BuilderWorkReceipt
→ Layer4Meter LCI
→ ReceiptOS Merkle root
→ Reality Compiler buyer packet
```

## Integration With CursorSwarm

Every agent cursor must have:

```text
cursor body
role menu
permission policy
receipt stream
approval gate
visible trail
```

Builder is the first cursor whose menu becomes real.

## Final Law

```text
The shell is real when the cursor can safely change a file, run a command, and prove both.
```

Or shorter:

```text
No actuator, no agent OS.
No receipt, no trust.
```
