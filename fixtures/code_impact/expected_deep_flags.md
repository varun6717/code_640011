# Expected deep pass + Flags — `code_impact` proof (TASK-041)

Proof for the **deep** mode + the **required Flags** output in
`core/skills/code_impact_assess.skill.md`: selective-read the flagged slice from `repo/`, trace the
real closure, emit Flags every run. Demonstrates a requirement that **ripples beyond the obvious
module** (routing → settlement).

**Inputs**
- Flagged slice (from the coarse pass, `expected_coarse_areas.md`): areas `routing`, `settlement`.
- Requirement: `code_impact.routing` — "impact on transaction routing to brand handlers" (adding/
  changing a card-brand routing path).
- Source: `runs/r-2026-06-17-001/repo/` (cloned from `fixtures/c_repo`, TASK-004/035) + map edges
  (TASK-005/036).

**Deep read (flagged slice only)**
- Read `src/routing/brand_router.c`, `route_table.c`, `brand_registry.c`, `config/brand_rules.c`
  (routing area) — **not** the whole repo.
- Closure trace from real code: `brand_router.c` `#include "reconciler.h"` and calls `reconcile_txn(t)`
  on the `TXN_SETTLE` path → edge `routing/brand_router → settlement/reconciler` (matches the map
  `depends_on`). Following it pulls `settlement/reconciler.c` into the slice. Upstream:
  `routing/brand_router` is `used_by` `transaction/txn_lifecycle`.

**Expected returned Flags (every run — here, one ripple)**

```yaml
flags:
  - type: scope_ripple
    area: settlement/reconciler
    finding: "brand_router.c calls reconcile_txn() on the settle path; brand routing is statically
      wired to settlement reconciliation (routing/brand_router -> settlement/reconciler)."
    implication: "Adding or changing a card-brand routing path also exercises settlement
      reconciliation — the change surface extends beyond the routing module."
    options: [include settlement in scope, phase settlement separately, adjust requirement, accept risk]
    recommended_option: "include settlement in scope"
    severity: material        # recommended: it moves the impacted code surface beyond routing
    requirement_ref: "code_impact.routing"
```

**Checks demonstrated**
- Deep reads **only the flagged slice** (routing + the settlement file the closure pulls in) — not the
  whole repo; transaction/errors/messaging/config-unrelated files stay unread.
- The closure is traced from **real code** (`reconcile_txn()` call), confirming the map edge — the
  ripple is grounded, not inferred from tags.
- **Flags emitted every run** (FR-BR-12): a clean requirement with no deviation would return
  `flags: []` + "no flags"; here the genuine routing→settlement coupling yields one `scope_ripple`.
- `severity: material` and `recommended_option` are **recommendations** — the skill **does not decide
  scope**; `brd_author`'s flag loop (TASK-042) surfaces this to the operator who decides.
- BRD code-impact section stays business-framed (impacted systems / scale / risk); the file/function
  detail above is carried to the FRD.
