# Working notes

## TASK-034 flags — RESOLVED 2026-06-22 (V-approved)

- **Flag A — `adapter` field (RESOLVED).** `change_type_assess.skill.md` no longer overwrites
  `adapter`; it stays `article_summarize` per §3.2 (the field records the *summarizing* adapter that
  authored the `descriptor`, not the last skill to touch the entry).
- **Flag B — PDF source label (RESOLVED).** Oracle provenance label reconciled `"pdf"` → `"sharepoint"`
  to match locked `UI_INPUT.example.yaml` + `brd_profile` routing sources. Run workspace + oracle
  realigned; selective-read routing verified to select doc sections.

## Open design question (from Flag B) — keeping provenance labels aligned, and non-PDF inputs

Flag B exposed that three axes are distinct and must stay aligned:

1. **source `type`** (`file | bitbucket | confluence | sharepoint`) — *how to ingest*; selects the
   connector (`ingest_<type>.py`). Covered by build check §10.4 (every configured type has a connector).
2. **source provenance label** (`source: sharepoint`) — *the logical bucket* entries are tagged with and
   that profiles route off (`section.sources`). **No build check guards this today** — a run can
   configure a `source:` label no profile section lists, and those entries route nowhere (silent).
3. **document format** (PDF / DOCX / HTML) — *how to extract structure*; owned by the docs_pipeline
   step-1 extraction skill (`pdf_extract`). Orthogonal to (1) and (2).

**Proposed alignment mechanism (P4/P5 build check — not built yet):** extend the domain-seam checks
with a *provenance-label containment* check, the source-label analogue of §10.1 topic containment:
assert every `section.sources[]` value across `brd_profile`/`frd_profile` is a recognized label, and
warn when a run's `UI_INPUT.sources[].source` is a label no section routes off ("ingested but
unroutable"). This makes Flag-B-style drift a loud build failure instead of a silent routing miss.

**On non-PDF inputs from SharePoint:** provenance (`sharepoint`) is independent of format. A `.docx`
from SharePoint keeps the same `source: sharepoint` label and routes identically — only docs_pipeline
**step 1** changes: generalize `pdf_extract` into a format-dispatching `doc_extract` (or add a sibling
extraction skill), leaving `article_summarize` / `change_type_assess` untouched. Same "write one more
extractor" seam pattern as the connectors. (Forward-compat note; deferred — see §11.)

## TASK-035 — clone idempotency caveat (open item, low priority)

D8b specifies clone idempotency as "re-clone/pull to pinned SHA; **skip if present & matching**."
`clone.py` instead implements **protective** idempotency: it raises `FileExistsError` on a populated
`repo/` (won't silently double-clone/clobber). The *skip-if-present* decision is the `source_processor`
worker's responsibility (orchestrator level) and isn't encoded in the skill yet. For the external build
the local fixture clones with `commit_sha: null`, so there is no SHA to "match" anyway — full D8b
skip-if-matching is a **port-time** behavior (real git repo + SHA). Recommend: add a worker-level
"repo/ present at pinned SHA → skip clone" check when repo SHAs become real. V to decide if/when.

## TASK-036 — finalization findings (for TASK-046)

1. **`load_domain_vocabulary` reads a hardcoded stub, not the YAML.** `core/extractors/__init__.py`
   returns `D5_PAYMENT_BRAND_VOCABULARY` (12 tags) and its docstring still says the YAML is "not yet
   present" — but `vocabulary.payment_brand.yaml` exists (TASK-014). Behaviorally correct today (stub ==
   YAML tag set; verified live at TASK-036), but a future vocab amendment would NOT propagate. TASK-046
   should wire the loader to read the YAML + correct the docstring.
2. **`vocab_sha` drift (low priority).** `onboarding_manifest.yaml` records `vocab_sha: d5frozen`, while
   CLAUDE.md's F1-reconciliation note says the YAML bumped to `d5frozen-r2` (emitted_by column fix; the
   12-tag SET is unchanged). Inert now (loader uses the stub, gate cache key is internally consistent at
   d5frozen), but it's the same disconnect as (1): the YAML's version isn't actually read. Reconcile when
   wiring (1).

Neither blocks TASK-036: code_map.json was produced, matches the oracle (0 per-file diffs; coverage 0.82),
and the gate/containment/adequacy checks pass live.

## TASK-037 — brd_author merge + discovery (foundation)

Created `core/skills/brd_author.skill.md` covering this task's portion: generic-engine framing
(FR-BR-01), the inline D2 baseline skeleton (no topics/must_capture), the deterministic baseline+profile
merge (by `id`: deep-merge / net-new insert by `position` / raise-not-lower `required` / exec summary
pinned + drafted last), and the discovery framing (load UI_INPUT + manifest → 2–3 questions → coarse
code pass map-only → then authoring) per FR-BR-02.

The per-section authoring loop, grounding/cite-or-flag, and revisit/shared-memory are present as named
stub sections pointing forward to **TASK-038** (selective routing §3.2 + coverage footer §3.7) and
**TASK-039** (FR-BR-05/06). The code-impact section carries a condensed pointer (deep pass + flag loop
land with TASK-041). This keeps the file a coherent, clean skill at every incremental step.

**Proof:** `fixtures/brd_author/expected_section_plan.md` — the deterministic 10-row ordered plan from
merging the payment_brand profile (TASK-015) over the baseline. `code_impact` lands at #6 (after
`requirements`, before `success_metrics`); `executive_summary` pinned to #10. Mirrored as a worked table
in the skill itself.

## TASK-038 — brd_author per-section authoring loop

Replaced the TASK-038 stub in `core/skills/brd_author.skill.md` with the full per-section loop:
(a) read profile entry → (b) selective routing per §3.2 — load entries where `source ∈ section.sources`
AND `topics ∩ section.topics ≠ ∅`, expand on demand, manifest always loaded, no load-all / no threshold
(FR-BR-04, NFR-05) → (c) draft against `must_capture` on the information hierarchy source → frame →
operator (FR-BR-03) → (d) probe gaps one topic at a time, gap-fills tied to unsatisfied requirements
(not 1:1 with files) → (e) per-section coverage footer `<!-- coverage: {topic: source|frame|operator|
open} -->` (§3.7), write incrementally. `code_impact` section routes to `code_map.json` + subagent, not
doc bodies. Cleaned the overview block's build-process phrasing.

Citation form + cite-or-flag (FR-BR-06) and revisit/shared-memory (FR-BR-05) remain stubs for **TASK-039**.

**Proof:** `fixtures/brd_author/expected_routing.md` — concrete routing trace over the real
`runs/r-2026-06-17-001/context_set/index.json` (TASK-034, 2 sharepoint files + bitbucket) × the
payment_brand profile. Shows §1 loads only P1 (not P2, though both are sharepoint) — routing is the
source∩topic intersection, not source alone; skeleton sections load nothing; `confluence` matches zero
this run (no confluence files) without error.

## TASK-039 — brd_author grounding (cite-or-flag) + revisit/shared-memory

Filled the last two stubs in `core/skills/brd_author.skill.md`, completing the skill:
- **Grounding (FR-BR-06):** inline citation tiers `[src: <provenance>]` / `[frame]` / `[operator]`
  matching the step-(c) hierarchy; cite-or-flag absolute — ungrounded `must_capture` → `[TBD —
  unsourced]` + coverage `open`, never invented. Citation tiers align with the footer's
  source/frame/operator values.
- **Revisiting & shared memory (FR-BR-05):** loop back to revise earlier sections (draft is mutable, not
  append-only); never re-ask an answered question (session + accumulating BRD.md carry answers; check
  draft before probing); mid-stage reset persists facts to the draft first, then resume reloads
  UI_INPUT + manifest + BRD.md (§3.5 / §16 authoring row).
Also cleaned a stray TASK-041 build-process reference in the code-impact pointer.

**Proof:** `fixtures/brd_author/expected_grounding.md` — a drafted `business_context` where `mandate` is
`[src: …]`-grounded and `brand_rules` is unsourced → `[TBD — unsourced]`; footer
`{mandate: source, brand_rules: open}` agrees with the inline tags.

**brd_author skill now complete** across TASK-037/038/039 (merge + discovery → per-section loop →
grounding + revisit). Remaining brd_author addition is the human-mediated flag loop (TASK-042).

## TASK-040 — code_impact coarse pass (map-only)

Created `core/skills/code_impact_assess.skill.md` with the **coarse** portion: read `code_map.json`
only (no source), match requirement `topics` × entry `tags` (same-vocabulary set-intersection) + a
`purpose` sweep, roll matched files up to module/area, rank by tag strength then purpose (required
topics outrank optional). Output = ranked **candidate areas** (NOT Flags) + rough risk read,
business-framed; threads into early BRD sections + sharpens discovery. Deep mode + required Flags
schema + output contract + handoff are forward stubs for **TASK-041**.

**Proof:** `fixtures/code_impact/expected_coarse_areas.md` — over the real
`runs/r-2026-06-17-001/context_set/code_map.json` (TASK-036) × the payment_brand `code_impact` topics
{routing, settlement}: areas rank routing (7 tag hits, required) > settlement (5 hits, optional);
non-matching modules excluded; the routing↔settlement ripple is explicitly NOT asserted (deep-pass
flag, TASK-041). No `repo/` source read.

## TASK-041 — code_impact deep pass + required Flags

Filled the deep-mode stub + added Output contract + Handoff + Boundaries in
`core/skills/code_impact_assess.skill.md`, completing the skill:
- **Deep:** selective-read the **flagged slice only** from `repo/`, trace the real `depends_on`/`used_by`
  closure (source confirms/extends the map edges; within-repo only, FR-DC-13), assess precise change.
- **Flags every run (FR-BR-12, D6b):** yaml schema `type / area / finding / implication / options /
  recommended_option / severity / requirement_ref`; `flags: []` + "no flags" when none. `severity`
  (material|advisory, D6c) and `recommended_option` are **recommendations** — never a scope decision.
- **Handoff:** returns summary + flags to brd_author; never writes BRD / edits repo / decides scope.

**Proof:** `fixtures/code_impact/expected_deep_flags.md` — the routing→settlement ripple, grounded in
real source: `brand_router.c` `#include "reconciler.h"` + `reconcile_txn()` on the settle path
(confirmed live in `repo/`), matching map edge `routing/brand_router → settlement/reconciler`. Yields one
`scope_ripple` flag (severity material, recommended); reads only the flagged slice; emitted-every-run
contract noted (clean req → `flags: []`).

**code_impact skill now complete** (TASK-040 coarse + TASK-041 deep). brd_author's consumption of these
flags = the human-mediated flag loop in **TASK-042**.

## TASK-042 — brd_author human-mediated flag loop + material threshold

Expanded the code-impact section in `core/skills/brd_author.skill.md` with the full GF flag loop
(FR-BR-08, FR-BR-13, D6c): delegate deep `code_impact` → draft business-framed → per flag, one at a
time: **surface** (finding/implication/options + recommended_option, recommend-not-decide) → **wait** →
**classify material vs advisory** by the D6c three-line test (operator's choice confirms the proposed
severity; can flip it either way) → **apply** (revise affected sections incl. earlier ones) →
**conditional re-run** (material → `code_impact` scoped to the *changed surface only*, FR-BR-13;
advisory → none) → **record** both ledgers: `decisions.flag(...)` + `telemetry.flag_decision(...)`
(concrete TASK-032 APIs). G1 is the backstop. No auto-applied scope change.

**Proof:** `fixtures/brd_author/expected_flag_loop.md` — the single TASK-041 routing→settlement
`scope_ripple` (proposed material) resolved two ways: "include settlement in scope" → material (adds a
module to in-scope) → revise + re-run over settlement only; "accept risk" → advisory (crosses no D6c
line) → record only, no re-run. Both show the exact ledger + telemetry writes.

brd_author skill: merge+discovery (037) + loop (038) + grounding/revisit (039) + flag loop (042) = the
authoring agent complete. Next BRD-layer task is **TASK-043** (brd_validator + G1).
