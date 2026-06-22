# Copilot overlay — VDI prerequisites (FR-XS-26)

These are **environment prerequisites**, not scaffold contents. The scaffolder does **not** emit
them; **Generate / onboarding surfaces them** so the operator (or central provisioning) ensures
they are in place before a Copilot run. This file documents them; it ships nothing executable.

## Terminal command-approval allow-list (the one that matters)

Copilot agent mode runs the plumbing scripts (`clone` / `ingest` / `hydrate` / `merge_manifest`)
as terminal commands. For a multi-step loop to proceed without per-command approval stalls, the
terminal **allow-list** must be set:

- `github.copilot.chat.agent.terminal.allowList` (or a blanket `chat.tools.terminal.autoApprove`)

**Scope = user, not workspace.** The VDI validation (`docs/COPILOT_VDI_VALIDATION.md`, PASSED
2026-06-16) found **workspace** `.vscode/settings.json` unreliable for these keys, while
**user-scope** settings took effect — so the allow-list's home is **user scope**, *not* the
workspace/scaffold (FR-XS-26). In production it MUST be **provisioned centrally** (MDM / managed
VS Code profile / VDI bootstrap).

> **Hard rule:** the scaffolder MUST NOT write these settings into the run scaffold. Emitting an
> allow-list into the workspace is both ineffective (wrong scope) and a policy footgun. Generate
> names it as a prerequisite; provisioning supplies it.

For **local / dev** toggling of the same user-scope keys, use the `max-autonomy` skill
(`maximum` / `balanced` / `safe default` / add-one-command) — a developer convenience, not the
production provisioning path.

## Agent mode itself

Copilot **agent mode** must be available/enabled in the VDI, and custom agents (`*.agent.md`) must
load and be invocable — both confirmed by the VDI validation (Checks 1–2). If agent mode is absent,
the Copilot path cannot run; that is an environment gate, not a scaffold defect.
