---
name: max-autonomy
type: Utility skill (user-invocable, environment setup) — contract, no external script
layer: Runtime-tool seam / bootstrap
consumes: VS Code USER settings.json
produces: updated user settings.json (+ one backup copy)
---

# Max Autonomy

## Role

You manage GitHub Copilot's **terminal auto-approval** in the operator's **VS Code USER
`settings.json`**, so the agent can run the pipeline's plumbing commands without stopping to
ask approval on every call.

This skill is a **contract**: the three presets below are exact JSON. "Balanced" means *exactly*
the balanced block — it does not drift run to run. You apply a preset by merging its block into
user settings yourself (in-editor); there is no external script. VS Code's own JSON language
server is your validator — a malformed edit is flagged live in the Problems panel.

**User scope only.** Target *user* settings, never workspace `.vscode/settings.json` — that scope
is unreliable for these keys and is often ignored or overridden by managed policy.

## When to run

- At session start, when the operator wants the agent to execute plumbing without per-command prompts.
- Any time the operator wants to change the autonomy level or add a single command.

## Modes

1. **maximum** — auto-approve (almost) everything + the blanket all-tools approval. Least friction,
   highest risk. **Applying this REQUIRES surfacing the risk statement (bottom of this file).**
2. **balanced** — auto-approve a curated set of safe dev commands; destructive commands stay gated.
   The recommended working default for the pipeline.
3. **safe default** — auto-approve only read-only commands; everything else prompts.
4. **add one command** — additive; add a single command to the current allow set (see below).

To **revert**, apply `safe default`, or remove the managed keys entirely (see *Managed keys*).

## Presets (the contract)

Applying a preset means: set these managed keys to *exactly* the values shown, replacing any prior
values, and leave every other setting (and all comments) untouched.

### balanced
```json
{
  "chat.tools.terminal.autoApprove": {
    "/^git\\s+(status|log|diff|show|branch)\\b/": true,
    "/^git\\s+(add|commit|fetch|remote)\\b/": true,
    "/^ls\\b/": true,
    "/^pwd\\b/": true,
    "/^cat\\b/": true,
    "/^echo\\b/": true,
    "/^which\\b/": true,
    "/^head\\b/": true,
    "/^tail\\b/": true,
    "/^python3?\\b/": true,
    "/^node\\b/": true,
    "/^npm\\s+(ci|install|test|run\\s+[\\w:-]+)\\b/": true,
    "/^pnpm\\s+(install|test)\\b/": true,
    "/^pip\\s+install\\b/": true,
    "/^mkdir\\b/": true,
    "/^bash\\s+scripts\\//": true,
    "/^rm\\b/": false,
    "/^sudo\\b/": false,
    "/^chmod\\b/": false,
    "/^chown\\b/": false,
    "/^kill\\b/": false,
    "/^dd\\b/": false,
    "/^mkfs\\b/": false,
    "/^mv\\b/": false,
    "/^git\\s+(push|reset|clean|checkout|rebase)\\b/": false,
    "/^npm\\s+publish\\b/": false,
    "/^curl\\b/": false,
    "/^wget\\b/": false,
    "/^shutdown\\b/": false,
    "/^reboot\\b/": false
  },
  "github.copilot.chat.agent.terminal.allowList": {
    "ls": true, "pwd": true, "cat": true, "echo": true, "which": true,
    "head": true, "tail": true, "mkdir": true, "node": true, "python3": true
  }
}
```
Also ensure `chat.tools.autoApprove` is **absent** (remove it if present).

### safe default
```json
{
  "chat.tools.terminal.autoApprove": {
    "/^git\\s+(status|log|diff|show)\\b/": true,
    "/^ls\\b/": true,
    "/^pwd\\b/": true,
    "/^cat\\b/": true,
    "/^echo\\b/": true,
    "/^which\\b/": true,
    "/^head\\b/": true,
    "/^tail\\b/": true,
    "/^rm\\b/": false,
    "/^sudo\\b/": false,
    "/^chmod\\b/": false,
    "/^chown\\b/": false,
    "/^kill\\b/": false,
    "/^dd\\b/": false,
    "/^mkfs\\b/": false,
    "/^git\\s+(push|reset|clean|checkout)\\b/": false,
    "/^curl\\b/": false,
    "/^wget\\b/": false
  },
  "github.copilot.chat.agent.terminal.allowList": {
    "ls": true, "pwd": true, "cat": true, "echo": true,
    "which": true, "head": true, "tail": true
  }
}
```
Also ensure `chat.tools.autoApprove` is **absent**.

### maximum
```json
{
  "chat.tools.terminal.autoApprove": {
    "/.*/": true,
    "/^rm\\b/": false,
    "/^sudo\\b/": false,
    "/^chmod\\b/": false,
    "/^chown\\b/": false,
    "/^kill\\b/": false,
    "/^dd\\b/": false,
    "/^mkfs\\b/": false,
    "/^git\\s+(push|reset|clean)\\b/": false,
    "/^shutdown\\b/": false,
    "/^reboot\\b/": false
  },
  "github.copilot.chat.agent.terminal.allowList": {
    "ls": true, "pwd": true, "cat": true, "echo": true, "which": true,
    "head": true, "tail": true, "mkdir": true, "node": true, "python3": true
  },
  "chat.tools.autoApprove": true
}
```
**Before applying, surface the risk statement at the bottom of this file, verbatim.**

## Add one command

To add a single command to the *current* configuration (leaving the rest as-is), insert one entry
into the existing `chat.tools.terminal.autoApprove` map:

- allow it:  `"<exact command>": true`   (e.g. `"docker ps": true`)
- gate it:   `"<exact command>": false`

Do not rebuild the whole map — add just the one key.

## How to apply

1. **Locate** the USER settings file:
   - Windows: `%APPDATA%\Code\User\settings.json`
   - macOS: `~/Library/Application Support/Code/User/settings.json`
   - Linux: `~/.config/Code/User/settings.json`
   - Or: Command Palette → *Preferences: Open User Settings (JSON)*.
2. **Refuse if broken.** If the file already shows JSON errors (Problems panel), STOP and ask the
   operator to fix it first — do not edit a file that doesn't already parse.
3. **Back up first.** Copy it to `settings.json.bak` before editing (one command, e.g. `cp`).
4. **Merge surgically.** Treat the file as JSONC — preserve all comments, formatting, and every
   other setting. Replace *only* the managed keys (below) with the chosen preset's values.
5. **Validate.** After saving, confirm VS Code shows **no JSON errors** for the file. If it does,
   restore `settings.json.bak` and report — never leave a broken settings file.
6. **Report.** State which preset was applied and that a backup exists. For `maximum`, confirm the
   operator saw the risk statement.

## Managed keys

This skill owns exactly these top-level keys:
- `chat.tools.terminal.autoApprove`
- `github.copilot.chat.agent.terminal.allowList`
- `chat.tools.autoApprove` (set only by `maximum`)

To fully revert, remove those three keys (back to VS Code's default prompting).

## If commands still prompt after applying

Key names differ across VS Code / Copilot versions. If the agent still prompts:
1. Open User Settings (JSON), search **"terminal auto approve"**, confirm which key your version honors.
2. Re-apply, or `add` the specific command, and verify a harmless allowed command runs without a prompt.

A managed/MDM policy can override user settings entirely; if so, the allow-list must be provisioned
centrally by the platform team — this skill can't force it locally.

## Risk statement (surface verbatim for `maximum`)

> ⚠  MAXIMUM autonomy. Copilot's agent will now run terminal commands — and, via
> `chat.tools.autoApprove`, other tool calls including file edits — without asking you to confirm
> each one. The deny entries are a coarse guardrail, NOT a security boundary: matching is
> prefix/literal and can be sidestepped (chained commands, argument variants), so a wrong or
> malicious command can execute before you can stop it. Use this only in a throwaway, sandboxed
> workspace with no production credentials, secrets, or write access to systems you care about —
> never point it at a repo wired to live infrastructure. Revert with `balanced` or `safe default`
> when you're done.
