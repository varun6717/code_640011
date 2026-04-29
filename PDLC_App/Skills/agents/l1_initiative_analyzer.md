# Initiative Analyzer

**Skill ID:** `l1_initiative_analyzer`
**Layer:** L1 — Strategy
**Type:** META · display-only
**Invoked by:** L1 Initiative Analysis screen
**Source:** PDLC_Platform_Design_Spec_v1.md

---

## Purpose

Display-only flow that orchestrates the per-initiative analysis sequence at L1.

## Input

- Initiative Project Card from L0
- Selected OKRs from OKR Lens

## Output

- UI flow diagram showing the orchestration; downstream skills are invoked in sequence

## Note — META skill (display-only)

**This skill is NOT sent to Claude.** It documents orchestration logic the platform code performs on the user's behalf, surfaced in the UI as a flow diagram or routing table. The content below describes what platform code does at this step, and which downstream skill(s) it invokes.

### Orchestration logic

For each initiative the Portfolio Lead drills into:
1. Invoke **OKR Scorer** with Project Card + selected OKRs → produces `okr_fit`.
2. Invoke **Market Scanner** (web search) with Project Card → produces `market_opportunity`.
3. Invoke **Competitor Scanner** (web search) with Project Card → produces `competitive_position`.
4. Invoke **Analysis Summarizer** with all three outputs → produces per-initiative summary card.

The three scoring skills run in parallel; Summarizer waits for all three. Per-dimension stale badges fire when underlying source changes (OKRs edited, allowlist updated, RSS feed refreshed).

## Rules

- Display-only: never sent to Claude as a prompt.
- Drives the per-initiative drill-in screen.
- Stale badges per dimension; manual reprocess.

## Related skills

- OKR Scorer, Market Scanner, Competitor Scanner, Analysis Summarizer

