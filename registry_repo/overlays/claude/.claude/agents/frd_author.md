---
name: frd_author
description: Interactive FRD authoring session — produces FRD.md from the accepted BRD.md, carrying detailed code impact forward; gate G2.
skill: core/skills/frd_author.skill.md
user_invocable: true
---

# frd_author — Claude overlay wrapper

Thin tool-specific wrapper (FR-XS-08, FR-XS-19, D9). **The logic is not here.** It lives in
the one shared skill; this file only points Claude at it and states how this overlay runs it.

**Load and execute `core/skills/frd_author.skill.md`** against this run's inputs
(the **accepted** `BRD.md` · `frd_profile.<domain>.yaml` · `context_set/`). Follow that skill
verbatim — do not restate, summarize, or fork its procedure here.

- **Executor:** your own **interactive session**, started by the operator via the `/start-frd`
  prompt file (`user_invocable: true`). You drive a chat with the operator.
- **Spine:** the FRD locks to the accepted `BRD.md` version (BRD-as-spine, FR-XS-14).
- **Gate:** produces `FRD.md`; `frd_validator` scores it → operator gate **G2**.
