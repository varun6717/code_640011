---
name: jira_validator
description: Subagent that checks jira_plan.json for bidirectional FRD↔Jira traceability, field completeness, and coverage; feeds gate G3. Deferred this slice.
skill: core/skills/jira_validator.skill.md
user_invocable: false
---

# jira_validator — Copilot overlay wrapper (`*.agent.md`)

Thin tool-specific wrapper (FR-XS-08, FR-XS-19, D9), native to Copilot agent mode. **The logic is
not here** — it lives in the one shared skill. Parity twin of the Claude
`.claude/agents/jira_validator.md` wrapper: same shared skill, native frontmatter + location.

**Load and execute `core/skills/jira_validator.skill.md`** against this run's inputs
(`jira_plan.json` · `FRD.md`). Follow that skill verbatim — do not restate, summarize, or fork
its procedure here.

- **Executor:** a **subagent** in its own context (`user_invocable: false`). Run autonomously and
  return a concise summary — do not start a chat.
- **Returns:** bidirectional traceability + field completeness + coverage that feed the single Jira
  push gate **G3** (you do not decide it).
- **Slice scope:** **deferred this slice** — present for overlay parity (D9), not invoked in the
  BRD→FRD run.
