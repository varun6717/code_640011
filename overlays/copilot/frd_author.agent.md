---
name: frd_author
description: Interactive FRD authoring agent — produces FRD.md from the accepted BRD.md, carrying detailed code impact forward; gate G2.
skill: core/skills/frd_author.skill.md
user_invocable: true
---

# frd_author — Copilot overlay wrapper (`*.agent.md`)

Thin tool-specific wrapper (FR-XS-08, FR-XS-19, D9), native to Copilot agent mode. **The logic is
not here** — it lives in the one shared skill. Parity twin of the Claude
`.claude/agents/frd_author.md` wrapper: same shared skill, native frontmatter + location.

**Load and execute `core/skills/frd_author.skill.md`** against this run's inputs
(the **accepted** `BRD.md` · `frd_profile.<domain>.yaml` · `context_set/`). Follow that skill
verbatim — do not restate, summarize, or fork its procedure here.

- **Executor:** an **interactive Copilot agent-mode session** the operator talks to directly
  (`user_invocable: true`), started via the `start-frd` prompt file.
- **Spine:** the FRD locks to the accepted `BRD.md` version (BRD-as-spine, FR-XS-14).
- **Gate:** produces `FRD.md`; `frd_validator` scores it → operator gate **G2**.
