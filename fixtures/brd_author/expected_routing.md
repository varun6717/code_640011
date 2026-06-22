# Expected selective routing — `brd_author` per-section loop proof (TASK-038)

Proof for step (b) selective routing (§3.2) in `core/skills/brd_author.skill.md`
§ "Per-section authoring loop". Demonstrates **always-selective** loading (FR-BR-04, NFR-05):
manifest always in view, only the per-section routed slice loaded, no load-all.

**Inputs**
- Manifest: `runs/r-2026-06-17-001/context_set/index.json` (TASK-034) — 2 sharepoint files +
  bitbucket (`code_map.json` built, TASK-036).
- Profile: `core/profiles/payment_brand/brd_profile.payment_brand.yaml` (TASK-015).

**Manifest entries**
- `P1` = `sharepoint/mastercard_mandate_part1_2026.md` — topics `{mandate, compliance_deadline,
  brand_rules, card_brand, certification}`
- `P2` = `sharepoint/mastercard_mandate_part2_2026.md` — topics `{message_format, interchange_fees,
  routing, reporting, compliance_deadline, card_brand}`

**Routing rule:** load entries where `source ∈ section.sources` **and** `topics ∩ section.topics ≠ ∅`.

| # | section                  | section.sources        | section.topics                  | loaded | why |
|---|--------------------------|------------------------|---------------------------------|--------|-----|
| 1 | business_context         | confluence, sharepoint | mandate, brand_rules            | P1     | P1∩={mandate,brand_rules}; P2∩=∅ |
| 2 | scope_objectives         | confluence, sharepoint | card_brand                      | P1, P2 | both carry card_brand |
| 3 | stakeholders             | —                      | — (skeleton)                    | none   | no topics → frame only |
| 4 | current_state            | —                      | — (skeleton)                    | none   | no topics → frame only |
| 5 | requirements             | confluence, sharepoint | certification, interchange_fees | P1, P2 | P1∩={certification}; P2∩={interchange_fees} |
| 6 | code_impact              | bitbucket              | routing, settlement             | code_map.json | code source → map + `code_impact` subagent, not doc bodies |
| 7 | success_metrics          | confluence, sharepoint | reporting                       | P2     | only P2 carries reporting |
| 8 | constraints_assumptions  | confluence, sharepoint | compliance_deadline             | P1, P2 | both carry compliance_deadline |
| 9 | out_of_scope             | —                      | — (skeleton)                    | none   | no topics → frame only |
|10 | executive_summary        | —                      | — (skeleton)                    | none   | synthesized last from the accumulated draft |

**Checks demonstrated**
- Selective by section: each section loads only its routed slice; no section loads all bodies, no
  threshold (FR-BR-04, NFR-05). `confluence` is in several `sources` lists but matches nothing this run
  (no confluence files) — correctly contributes zero loads, not an error.
- Routing is the **intersection** of source AND topic, not source alone: §1 loads P1 but not P2 though
  both are `sharepoint`.
- Coverage footer per section values each topic by tier, e.g. for §1 once drafted:
  `<!-- coverage: {mandate: source, brand_rules: source} -->`.
- `code_impact` (§6) routes to `bitbucket` → `code_map.json` + subagent, never document bodies.
