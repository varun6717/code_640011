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
