# fixtures/mixed_repo — polyglot dispatch test bed (ADR-002)

A deliberately **multi-language** repo for exercising per-language partition dispatch
(ADR-002). It is **separate** from `fixtures/c_repo/` on purpose: `c_repo` carries the
human-signed-off `expected_code_map.json` oracle (TASK-005) and must stay pristine, so
polyglot behavior is proven here instead.

## Layout

```
src/routing/router.c      ┐
src/routing/router.h      ├─ C — the majority language (→ frozen tree-sitter-c extractor, TASK-009)
src/config/config.c       ┘
scripts/report.py            Python — residue (→ model fallback, marked coarse, TASK-010)
tools/Validate.java          Java   — residue (→ model fallback, marked coarse, TASK-010)
```

## What it proves (TASK-010)

- `detect_language(.)` → **`c`** (majority); top-level `code_map.language = "c"`.
- `partition_by_language(.)` → `{c: [3 files], python: [report.py], java: [Validate.java]}`.
- Dispatch routes the **C partition** through the deterministic extractor (full coverage)
  and the **Python + Java residue** through the model fallback (`coverage: coarse`).
- Residue files count as `files_fallback` in `coverage_report`, so `coverage` reflects the
  deterministic share — and a residue-heavy variant would trip the 0.80 floor →
  `REONBOARD_FLAG` (TASK-013) naming the un-onboarded language. No file is dropped.

This fixture intentionally has **no signed oracle** — it is a behavioral test bed for the
fallback path, not a regression oracle for the C extractor.
