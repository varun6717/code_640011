# Copilot / VDI Validation Runbook

**Project:** PDLC_App_v2 · JPMC Merchant Services · AI Automation
**Validates:** Requirements D10 / `FR-XS-22`, `FR-XS-23`, `FR-XS-24`
**Companion to:** `REQUIREMENTS.md`
**Run when:** Early — before the Copilot overlay work depends on agent-mode command execution.
**Est. time:** 45–90 min in the target VDI.

---

## 0. What this proves (and what it doesn't)

This is a **validation task, not a feasibility gate.** The architecture treats Claude Code and Copilot as co-equal MVP paths; this runbook confirms the one environment-dependent unknown — whether the **VDI's command-approval policy** lets a Copilot agent run terminal commands (a hello-world script, then a short multi-command sequence) without per-command approval stalling the loop — plus four supporting agent-mode behaviors. **No real skills, sources, or repos are involved**; the scripts are deliberately dead-simple so the only thing under test is command execution and approval.

**Outcomes and what each means:**
- **PASS** — Copilot path is confirmed co-equal; proceed with the Copilot overlay as planned.
- **PARTIAL (approval friction)** — capability works but the agent stalls on per-command approval → resolved by **tuning the allow-list** (Check 3). Not a blocker.
- **HARD BLOCK** — managed VDI policy forbids the agent from executing terminal commands *and* the allow-list/auto-approve settings are locked → escalate; only this outcome demotes Copilot from MVP (record it, feed back to D10).

> **Governance note (Rule 1).** This runbook is a foundational de-risking artifact. If its result becomes a canonical phase task, slotting it in with `TASK-NNN` metadata is the **Task Manager**'s call, not this runbook's.

---

## 1. Preconditions

- Target **JPMC VDI** with **VS Code** + **GitHub Copilot Chat** extension installed.
- Copilot **agent mode** present (Chat view → mode selector shows *Agent*). If absent, stop at Check 1.
- Permission to edit **workspace** `.vscode/settings.json` (and ideally user settings).
- Python 3 and `git` available on PATH in the VDI terminal.
- A scratch folder you can delete afterward (no real repo or secrets needed — fixtures are no-ops).

---

## 2. Build the test scaffold

Create this throwaway tree. The scripts are dead-simple (a hello-world and a one-line "step" printer) — they exist only to exercise *command execution and approval*, **not** any real ingestion, sources, or skills:

```
copilot-validate/
├─ .github/
│  ├─ copilot-instructions.md
│  ├─ agents/
│  │  ├─ worker.agent.md
│  │  └─ demo_author.agent.md
│  └─ prompts/
│     ├─ start-validate.prompt.md
│     └─ start-frd.prompt.md
├─ .vscode/
│  └─ settings.json
├─ scripts/
│  ├─ hello.py
│  └─ step.py
└─ UI_INPUT.yaml
```

### 2.0 How to create these files

Two options:
- **Recommended — have the Copilot agent create them (this also tests file-write).** In agent mode, attach/paste this runbook and say: *"Create a new `copilot-validate/` folder and write the files exactly as specified in §2.1–§2.11."* Approve the file writes when prompted.
- **By hand** — create each file from §2.1–§2.11.

**Critical ordering — don't skip.** `.vscode/settings.json` (§2.5) governs command approval, and **a settings change only takes effect after a window reload.** So:
1. Create all files, including `.vscode/settings.json`.
2. **Reload the window** — Command Palette → *Developer: Reload Window*. (This ends the current chat session — expected.)
3. Open a **fresh agent thread**, then run the Checks (`/start-validate`).

If you write `settings.json` but skip the reload, you'll see approval prompts the allow-list would have suppressed — a false PARTIAL on Check 3. (Note: writing `settings.json` is a *file edit*, a different approval path than running terminal commands — so the agent creating it does **not** pre-answer Check 3; Check 3 still tests whether the resulting allow-list suppresses the *terminal* prompts.)

### 2.1 `scripts/hello.py`
```python
import sys
label = sys.argv[1] if len(sys.argv) > 1 else "world"
print(f"[hello] hello {label} from python3 — command executed OK")
```

### 2.2 `scripts/step.py`
```python
import sys
n = sys.argv[1] if len(sys.argv) > 1 else "?"
print(f"[step {n}] ok")
```

### 2.5 `.vscode/settings.json` (the allow-list — the heart of Check 3)

**This is the *persistent, across-sessions* control** — the thing that replaces clicking **"Allow all in this session"** on every new chat thread. It matters here because the platform opens a **new thread at each stage boundary** (BRD → FRD → Jira), so a session-scoped "Allow all" would have to be re-clicked each stage; the allow-list below survives across threads and names specific commands (auditable — important in a regulated VDI). Remember it only activates after a **window reload** (§2.0).

```json
{
  "github.copilot.chat.agent.terminal.allowList": {
    "bash": true,
    "git": true,
    "python3": true,
    "python": true,
    "echo": true,
    "mkdir": true,
    "ls": true,
    "cat": true
  },
  "github.copilot.chat.agent.terminal.denyList": {
    "rm": true,
    "curl": true,
    "wget": true,
    "chmod": true,
    "kill": true
  }
}
```
> The exact setting **key varies by VS Code / Copilot version.** If the keys above don't resolve, open Settings (UI) and search **"terminal auto approve"** / **"allow list"**, and also try the alternates `chat.tools.terminal.autoApprove` (boolean blanket) and `github.copilot.chat.tools.terminal.allowlist`. Record which namespace your VDI version uses.

### 2.6 `.github/copilot-instructions.md`
```markdown
# Validation orchestrator
You are the orchestrator for a connectivity test. You delegate to native subagents and
call scripts in `scripts/` as tool calls. Do not do the script work yourself.

On `/start-validate`:
1. Read `UI_INPUT.yaml`.
2. Run, as a single terminal command: `python3 scripts/hello.py`
3. Run, in sequence, as three separate terminal commands (this tests whether each step
   re-prompts for approval): `python3 scripts/step.py 1`, then `python3 scripts/step.py 2`,
   then `python3 scripts/step.py 3`.
4. Delegate to **parallel `worker` subagents**, one per label in `UI_INPUT.yaml.labels` —
   run these as parallel subagents; each returns a one-line summary.
5. Report: which commands ran, whether any required manual approval, and the subagent summaries.
```

### 2.7 `.github/agents/worker.agent.md`
```markdown
---
name: worker
description: Generic subagent-only worker (validation stub — no real work).
user-invocable: false
model: <default>
tools: [terminal]
---
You are a subagent-only worker. For the single label handed to you, run
`python3 scripts/hello.py <label>` and return one line: "<label>: ok".
```

### 2.8 `.github/agents/demo_author.agent.md`
```markdown
---
name: demo_author
description: Interactive role (validation stub) — confirms user-invocable roles load.
user-invocable: true
model: <default>
tools: [terminal]
---
You are an interactive, user-invocable role. When invoked, greet and state you loaded
as a user-invocable agent, then stop.
```

### 2.9 `.github/prompts/start-validate.prompt.md`
```markdown
---
mode: agent
description: Kicks off the connectivity validation run.
---
Begin the validation run per copilot-instructions.md. Point yourself at UI_INPUT.yaml.
```

### 2.10 `.github/prompts/start-frd.prompt.md`
```markdown
---
mode: agent
description: Fresh-context stage entry (validation stub).
---
You are entering a fresh stage. Re-orient ONLY from UI_INPUT.yaml. State what you
loaded, then stop. (Then, for Check 3 persistence: run `python3 scripts/hello.py` and
note whether it prompts for approval in this new thread.)
```

### 2.11 `UI_INPUT.yaml`
```yaml
run_id: validate-001
runtime_tool: copilot
labels: [alpha, beta]          # generic fan-out targets — NOT real sources
note: Connectivity test only. No real domain, skills, sources, or repos involved.
```

---

## 3. The checks

Run each in order. Record PASS / PARTIAL / FAIL + notes in §4.

### Check 1 — Agent mode available
**Do:** Open the `copilot-validate/` folder in VS Code. Open Copilot Chat → mode selector.
**Pass:** *Agent* mode is selectable. Note the **models** offered (GPT-family / Claude).
**If fail:** Agent mode disabled by policy → **HARD BLOCK** at the platform level; stop and escalate.

### Check 2 — Custom agents/subagents load
**Do:** In agent mode, type `@` (or the invoke gesture) and look for `demo_author`. Invoke it.
**Pass:** `demo_author` is invocable and replies that it loaded as user-invocable; `worker` does **not** appear as user-invocable (worker-only). This confirms the wrapper frontmatter (`user-invocable`) is honored and the `agents/` location is read.
**If fail:** Note whether the issue is location (`agents/` not scanned) or frontmatter parsing — feeds overlay authoring (D9).

### Check 3 — Command-approval policy *(the decisive one)*
**Do:** Ensure `.vscode/settings.json` (§2.5) is in place **and you've reloaded the window** (§2.0). In a **fresh agent thread**, run `/start-validate`. Watch the hello-world command and the three-step sequence execute.

**Two approval mechanisms — know which you're seeing:**
- *Session-scoped* — clicking **"Allow all in this session"** on the prompt suppresses further prompts for **that thread only**; it resets on a new thread. Fine for a one-off, but the platform starts a new thread per stage.
- *Persistent* — the §2.5 allow-list suppresses prompts for the named commands **across all threads**. This is what Check 3 is really testing.

**Pass:** With the allow-list set + window reloaded, `python3 scripts/hello.py` prints its line and the `step.py 1/2/3` sequence runs to completion — **without any approval prompt** (you did *not* have to click "Allow all"). The multi-command sequence is the real test: each step should run without re-prompting. Persistence is then re-confirmed in Check 5 — after `Ctrl+N`, `hello.py` still runs without a prompt.
**Partial:** Prompts still appear per command (allow-list not taking effect) → (a) confirm the correct setting key for your version (§2.5 note) and reload again; (b) verify **"Allow all in this session"** *does* suppress prompts for the thread — if it does, the **capability is fine and only persistence is the gap**, which is acceptable for MVP (operator clicks once per stage); (c) test-only, set `chat.tools.terminal.autoApprove: true` to isolate config-vs-policy. Record which path worked.
**Fail / HARD BLOCK:** Even "Allow all in this session" is unavailable and commands are blocked, with allow-list / auto-approve greyed out or overridden by managed policy → record the policy source (workspace / user / device-managed) and escalate. *This is the only outcome that demotes Copilot.*

### Check 4 — Parallel fan-out
**Do:** Observe step 4 of the run (the `worker` delegation over the labels `alpha` + `beta`).
**Pass:** Two subagents run as **isolated, collapsible tool calls**; ideally concurrently. Each returns "<label>: ok".
**Partial:** They run but **serialize** (one after another). Acceptable for MVP correctness; note it — coordinator phrasing may need tuning, and throughput expectations adjust.
**If fail:** Delegation doesn't spawn subagents at all → note; affects the fan-out design for the Copilot overlay.

### Check 5 — Stage transition / fresh context
**Do:** Press `Ctrl+N` (new chat thread). Run `/start-frd`.
**Pass:** A clean thread with no carryover from the validation run; the agent re-orients only from `UI_INPUT.yaml` and reports what it loaded.
**If fail:** Note whether new-thread doesn't clear context or the prompt file isn't picked up.

---

## 4. Results capture

| Check | Result (PASS/PARTIAL/FAIL) | Setting key used (Ch.3) | Notes |
|-------|----------------------------|-------------------------|-------|
| 1 — Agent mode |  |  | Models offered: |
| 2 — Custom agents |  | — |  |
| 3 — Command approval |  |  | Policy source if blocked: |
| 4 — Parallel fan-out |  | — | Concurrent / serialized: |
| 5 — Stage transition |  | — |  |

**Overall outcome (circle one):**  PASS  ·  PARTIAL (allow-list tuning)  ·  HARD BLOCK

**Decision fed back to D10 / `FR-XS-24`:**
_____________________________________________________________________

**VS Code version / Copilot extension version:** _______________________

---

## 5. Settings reference (notes)

- **Allow-list (recommended for a regulated VDI):** `github.copilot.chat.agent.terminal.allowList` — an object map of approved command prefixes; positive control, safest. Keep destructive commands in `denyList`.
- **Blanket auto-approve (test/trusted only):** `chat.tools.terminal.autoApprove: true` — approves *all* commands; use only to isolate whether the block is policy vs config, not as the production setting.
- **Deny-list caveat:** matching is prefix-ish and **not a hard security boundary** (e.g. denying `ls -l` may not stop `ls -la`). Rely on the allow-list as the positive control, deny-list only for obvious destructive verbs.
- **Experimental / version drift:** auto-approve + allow/deny lists are recent and the exact keys have shifted across VS Code releases — always confirm the live key via Settings search in your VDI's version.
- **Managed policy:** in a locked VDI these keys may be centrally managed and non-overridable. If so, that's the HARD-BLOCK signal — capture *where* the override comes from (device management vs admin profile) for the escalation.
