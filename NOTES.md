# Working notes — open flags for V

## TASK-034 surfaced two fixture/contract drifts (2026-06-22) — awaiting V decision

Both were found running the doc pipeline over the PDF fixtures. The produced `index.json` entries
match `fixtures/pdf/expected_manifest_entries.json` exactly on content (topics, change_type,
descriptor, adapter), so TASK-034 acceptance is met — but two upstream inconsistencies should be
reconciled before the spine relies on them. Surfacing, not silently picking (cite-or-flag; F1 pattern).

### Flag A — `adapter` field: skill says one thing, spec + oracle say another
- `change_type_assess.skill.md` (TASK-019) instructs: *"set `adapter: change_type_assess` to record
  the last skill that touched the entry."*
- BUT `docs/TECH_SPEC.md` section 3.2's normative example AND the signed-off oracle both pin
  `adapter: article_summarize` on an entry that already carries a `change_type` and change_type_assess
  topics (e.g. `compliance_deadline`). So 3.2 treats `adapter` as *the summarizing adapter that
  authored the entry's descriptor*, not *last skill touched*.
- Recommendation: `change_type_assess` should NOT overwrite `adapter` — leave it `article_summarize`
  (matches 3.2 + oracle). One-line fix to the skill's Output/Rules. V to approve.

### Flag B — PDF source label: oracle "pdf" vs locked UI_INPUT "sharepoint"
- Oracle (`expected_manifest_entries.json`) labels the PDF source "pdf" (path `context_set/pdf/...`).
- Locked `fixtures/UI_INPUT.example.yaml` (TASK-002) labels that same PDF `source: sharepoint`.
- `brd_profile.payment_brand.yaml` routes doc sections off `sources: [confluence, sharepoint]`.
- Consequence (verified): selective-read predicate `source in section.sources AND topics intersect
  section.topics` selects NOTHING under "pdf", but routes correctly into 4 doc sections under
  "sharepoint".
- Recommendation: reconcile the oracle's provenance label to "sharepoint" (the locked config value)
  so the grading fixture and a real wired run agree and routing works. V to approve.
  (TASK-034 run workspace currently mirrors the oracle's "pdf" label verbatim for a clean content
  diff; the routing demo shows both labels.)
