# Intake Router

**Skill ID:** `l0_intake_router`
**Layer:** L0 — Intake
**Type:** META · display-only
**Invoked by:** Sponsor selection on L0 Project Type screen
**Source:** PDLC_Platform_Design_Spec_v1.md

---

## Purpose

Routes the Sponsor's selected project type (one of 7 themes) to the corresponding Theme Template for the Intake Chat.

## Input

- Selected theme: one of `aiml | compliance | product | platform | data | automation | migration`

## Output

- Theme Template file reference (e.g., `l0_intake_aiml.md`) loaded into the Intake Chat session

## Note — META skill (display-only)

**This skill is NOT sent to Claude.** It documents orchestration logic the platform code performs on the user's behalf, surfaced in the UI as a flow diagram or routing table. The content below describes what platform code does at this step, and which downstream skill(s) it invokes.

### Orchestration logic

1. Receive the theme selection from the L0 Project Type screen.
2. Look up the corresponding Theme Template file in `.github/agents/`:
   - `aiml`        → `l0_intake_aiml.md`
   - `compliance`  → `l0_intake_compliance.md`
   - `product`     → `l0_intake_product.md`
   - `platform`    → `l0_intake_platform.md`
   - `data`        → `l0_intake_data.md`
   - `automation`  → `l0_intake_automation.md`
   - `migration`   → `l0_intake_migration.md`
3. Pass the file as the system prompt to the Intake Chat session.
4. Log the routing decision to the audit trail.

## Rules

- Display-only: never sent to Claude as a prompt.
- Pattern A — universal questions are duplicated in each Theme Template, not extracted.
- Theme cannot be changed mid-Intake without abandoning the chat (it would change the prompt mid-conversation).

## Related skills

- Theme Templates (×7) — `l0_intake_<theme>.md`
- Project Summarizer — consumes the Intake Chat transcript

