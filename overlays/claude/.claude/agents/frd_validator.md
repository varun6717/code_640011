---
name: frd_validator
description: Subagent that scores FRD.md for BRD→FRD traceability and testability and returns a score + gap list; feeds gate G2.
skill: core/skills/frd_validator.skill.md
user_invocable: false
---

# frd_validator — Claude overlay wrapper

Thin tool-specific wrapper (FR-XS-08, FR-XS-19, D9). **The logic is not here.** It lives in
the one shared skill; this file only points Claude at it and states how this overlay runs it.

**Load and execute `core/skills/frd_validator.skill.md`** against this run's inputs
(`FRD.md` · the accepted `BRD.md`). Follow that skill verbatim — do not restate, summarize, or
fork its procedure here.

- **Executor:** **subagent** in its own context window (`user_invocable: false`), spawned by the
  orchestrator or `frd_author`. Run autonomously and return a concise summary — do not start a chat.
- **Returns:** a score + BRD→FRD traceability + testability gaps that feed the operator gate **G2**.
