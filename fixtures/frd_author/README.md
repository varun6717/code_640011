# `frd_author` fixture — accepted-BRD → FRD proof (TASK-044)

Proof for `core/skills/frd_author.skill.md`: consume an **accepted BRD vN**, translate it into a
functional decomposition, **carry the file/function detail forward** (FR-FR-03), make every FRD topic
**`traces_to`** a real BRD anchor (FR-FR-06), and **pin to BRD vN** (FR-XS-14).

**Inputs**
- **Accepted BRD:** `fixtures/brd_validator/brd_pass.md` — the BRD that passed G1 (TASK-043), locked
  as **BRD v1**. Its sections/anchors: `business_context.{mandate,brand_rules}`,
  `scope_objectives.card_brand`, `requirements.{certification,interchange_fees}`,
  `code_impact.{routing,settlement}`, `success_metrics.reporting`,
  `constraints_assumptions.compliance_deadline`. Its code-impact section is **business-framed** and the
  routing→settlement ripple was **dispositioned in-scope** (the locked surface).
- **Deep code detail:** `fixtures/code_impact/expected_deep_flags.md` (TASK-041) — the file/function
  detail the BRD intentionally omitted: `src/routing/brand_router.c` calls `reconcile_txn()` on the
  `TXN_SETTLE` path; edge `routing/brand_router → settlement/reconciler`.
- **Profile:** `core/profiles/payment_brand/frd_profile.payment_brand.yaml` (TASK-016).

**Merged authoring plan** (no net-new sections; baseline order): `actor_flows` → `system_behaviors` →
`data_contracts` → `error_states` → `nfrs` → `traceability` → `executive_summary` (last).

`expected_frd.md` shows the proof-bearing excerpts. What each demonstrates:

- **Header pins BRD v1** — `<!-- pinned_brd: v1 -->`, read from the G1 `gate` record
  (`outcome: accept, version: 1`) in `decisions.jsonl` (FR-FR-02, FR-XS-14).
- **FR-FR-03 — file/function detail carried forward.** `system_behaviors.routing` and `error_states`
  state `brand_router.c` / `reconcile_txn()` / the `TXN_SETTLE` path — detail absent from the
  business-framed BRD, recovered by reading `code_map.json` + `repo/` for the **already-agreed** surface
  (scope is *not* re-decided; the BRD locked it at G1).
- **FR-FR-06 — `traces_to` resolves.** Every topic's `traces_to` points at a real BRD anchor; the
  trailing `<!-- traces: {...} -->` block is the machine-checkable map `frd_validator` parses at G2.
- **Testability by `functional_kind` (§9.3).** `system_behaviors` carries **acceptance criteria**;
  `nfrs.certification` carries a **measurable target** (suite + pass threshold), not acceptance criteria.
- **Every BRD requirement traced or out-of-scope (G2 hard rule).** `interchange_fees` and
  `compliance_deadline` have no functional behavior → marked **out-of-scope** in the traces block;
  every other BRD topic is traced by ≥1 FRD topic.
