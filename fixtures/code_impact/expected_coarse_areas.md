# Expected coarse match — `code_impact` map-only proof (TASK-040)

Proof for the **coarse** mode in `core/skills/code_impact_assess.skill.md`: requirement topics ×
`code_map.json` `tags`/`purpose` → ranked **candidate areas** (not yet Flags), reading the **map only**.

**Inputs**
- Map: `runs/r-2026-06-17-001/context_set/code_map.json` (TASK-036; 34 files, coarse, 0.82).
- Requirement: the `code_impact` section of `brd_profile.payment_brand.yaml` (TASK-015), topics
  `{routing, settlement}`.

**Match — `entry.tags ∩ {routing, settlement} ≠ ∅`, rolled up to module**

| rank | area (module) | matched files (tag hits)                                                                 | tags matched      | purpose (from map) |
|------|---------------|-------------------------------------------------------------------------------------------|-------------------|--------------------|
| 1 | routing    | brand_registry.c, brand_router.c, capture_route.c, dispatch.c, route_table.c/.h, routing.h | routing (×7)      | Dispatches a transaction to the correct card-brand handler |
| 2 | settlement | batch.h, ledger_post.c, reconciler.c/.h, settlement_batch.c                                | settlement (×5)   | Reconciliation, batching, and ledger posting of settled transactions |

Ranking: `routing` outranks `settlement` — the section's **required** topic is `routing` and its module
carries the most/strongest tag hits; `settlement` (`required: false`) is the secondary candidate.

**Purpose sweep:** the `routing` component purpose ("…correct card-brand handler") reinforces the topic
hit; no purpose-only area surfaces here beyond the two tag-matched modules. Modules with no
`{routing, settlement}` tag (transaction, errors, messaging, config, shared, vendor) are **not**
candidates this pass.

**Checks demonstrated**
- Map-only: every column above is derived from `code_map.json` — **no source file under `repo/` is read**
  (FR-BR-07 coarse contract; acceptance: coarse mode reads no source files).
- Output is **candidate areas, not Flags** — e.g. the routing↔settlement shared-dependency *ripple* is
  NOT asserted here; that is a deep-pass divergence flag (TASK-041), reached only by reading real code.
- Areas are modules/components (rolled up from files), ranked by tag strength then purpose, with required
  topics outranking optional — these thread into the early BRD sections and seed the deep pass's scope.
