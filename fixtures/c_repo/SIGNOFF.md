# SIGNOFF.md — `expected_code_map.json` (TASK-005 regression oracle)

This file records the **human sign-off** that makes `expected_code_map.json` the trusted
grading oracle for TASK-012 (validate the frozen C extractor) and TASK-013 (3-branch gate).
Per TASK-005 acceptance, the oracle is **not** model-self-generated/self-graded: it was
hand-authored by reading the fixture source directly (not by running any extractor, which does
not yet exist), and is valid only once a human signs below.

## What was authored against what

- **Oracle:** `fixtures/c_repo/expected_code_map.json`
- **Fixture state (frozen):** `fixtures/c_repo/**` at commit **`e94c70d`**
  ("TASK-004: finalize brand_rules.c macro-param rename (freeze fixture for oracle)").
- **Contracts:** `docs/TECH_SPEC.md` §3.3 (`code_map.json` schema + `coverage_report`), §5.4/§5.5
  (coverage formula, normalization), `docs/REQUIREMENTS.md` D5 (tag vocabulary), D6a.
- **Source basis:** `fixtures/c_repo/PATTERN_CATALOG.md` (the TASK-004 tier/edge inventory),
  cross-checked against every `.c`/`.h` file.

## Authoring decisions (pinned)

1. **Per-file `coverage` is `coarse` for all 34 files; top-level `coverage` is `coarse`.**
   Rationale: §5.5 line 474 — the deterministic extractor emits `coarse` ("deep pass confirms");
   the §3.3 + D6a normative examples show cleanly-extracted files as `coarse`; `deep` is only ever
   produced by the Stage-2 deep pass (§5.6), which the extractor graded here does not run. The
   `PATTERN_CATALOG.md` §3 labels of "coverage: deep" describe deep-*eligibility* (the bucket def
   hedges "deep candidate"), not extractor output. Confirmed by operator (V), 2026-06-19.

2. **The extracted / fallback / unresolved distinction lives only in `coverage_report`**, not as a
   per-file field (§3.3 has no per-file bucket field). The per-file signal for an unresolved file is
   its **under-reported `interfaces[]`** (e.g. `config/brand_rules.c` lists only `get_brand_rule` —
   the macro-generated `*_route` functions are invisible to ctags and therefore absent).

3. **Volatile top-level fields are informational, NOT part of the structural comparison.**
   TASK-012 must compare `files[]` structural fields (`path/module/interfaces/depends_on/used_by/
   coverage`) + `coverage_report`, and **ignore**: `commit_sha`, `generated_at`, `seal_id`,
   `built_with_extractor_sha`. The latter is set to `PENDING_TASK_012_FREEZE` because the extractor
   SHA does not exist until the freeze at TASK-012.

## Deltas from `PATTERN_CATALOG.md` (surfaced, not silently resolved)

- **D-1 (corrected in oracle): missing `txn_lifecycle → txn_state` edge.** The catalog (§3 edge
  table, §5 used_by) treats `transaction/txn_state` as having no in-tree caller. But
  `src/transaction/txn_lifecycle.c` calls `txn_advance()` (defined in `txn_state.c`) — a clean,
  statically-resolvable edge cscope would find. The oracle therefore includes
  `transaction/txn_lifecycle` `depends_on` `transaction/txn_state` and the reverse `used_by`.
  **Recommend** patching `PATTERN_CATALOG.md` §3/§5 to match.

- **D-2 (wording only): "coverage: deep" labels.** `PATTERN_CATALOG.md` §3 labels Tier-1 files
  "coverage: deep". Per decision #1 the oracle marks them `coarse`. **Recommend** softening the
  catalog wording to "deep-eligible" to prevent confusing TASK-009/012.

## Validation run (2026-06-19)

`expected_code_map.json` passed automated checks: valid JSON; 34 file entries; all `tags ⊆ D5
vocabulary`; reserved `external_calls`/`exposes` empty on every file; per-file + top-level
`coverage = coarse`; `coverage_report` buckets sum to `files_seen` (28+3+3=34) and
`28/34 = 0.82 ≥ 0.80` floor; `depends_on ↔ used_by` fully bidirectional (19/19 edges).

## Sign-off

By signing, the operator confirms the tier assignments, edge tables, `interfaces[]`, tag
assignments, and the `coverage_report` summary are correct, and that this oracle may grade the
frozen extractor at TASK-012.

- **Signed off by:** V   _(operator)_
- **Date:** 2026-06-19
- **Fixture commit signed against:** `e94c70d`

> Status: **SIGNED OFF** by operator V, 2026-06-19. Authored by Claude (TASK-005), 2026-06-19.
> Catalog deltas D-1 and D-2 patched into `PATTERN_CATALOG.md` in the same commit.
