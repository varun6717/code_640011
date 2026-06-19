---
name: code_map_build
type: Pre-processing skill (shared core; code_pipeline entry)
layer: Data & context
consumes: repo/ (cloned repo)
produces: context_set/code_map.json
runs: once per repo · requirement-independent · cached (§5.3 gate)
extractor_seam: core/extractors/  (deterministic, frozen; this skill consumes, never modifies)
---

# Code Map Build

## Role

You build a **coarse, navigable index** of an already-cloned codebase. Code is handled differently from
documents: the full repo lives on disk in `repo/` and is read natively on demand — you do **not**
summarize all the code. You produce a lightweight `code_map.json` (§3.3) that lets later steps (coarse
impact, deep impact) find and pull the right files.

Ingestion (the `git clone` into `repo/`) is done by a script before you run. Your job is the map.

## Principle — coarse-first, deep-on-demand, language-agnostic

Do **not** read every file. Build a module/file-level map; fine (function-level) detail is read later,
on demand, only for the slice an impact assessment points at.
- **Language-agnostic via one seam.** Language varies in exactly one place — the per-language extractor
  under `core/extractors/` (§5.5). The dispatcher routes to it; the core, the schema, and `code_impact`
  never change when a language is added.
- Start from the **file tree** and **entry points** (cheap) to establish module structure.
- **Deterministic tooling owns structure; the model owns meaning.** The extractor (e.g. `tree-sitter` for
  C per ADR-001) pulls structural fields and edges mechanically. The per-language extractor is
  **onboarded once and frozen** (human-gated); this skill **consumes** it and does **not** generate or
  modify it at map-build runtime (FR-DC-14…17). When no frozen extractor exists for a language, fall back
  to model-derived structure and mark it lower-coverage (TASK-010).
- **Bound context — never load the whole repo.** Structure is carried by tooling; the model is reserved
  for the bounded `purpose`/`tags` summarization it is actually good at.
- Summarize at **module/file** granularity and capture **dependency edges** — they make this an *impact*
  map, not a flat summary. Edge resolution is a deterministic **merge step** over the collected entries
  (`merge_edges`), not a single file's judgment.

---

## Dispatch — the deterministic spine (TASK-008)

The dispatch flow is **deterministic and model-free** (FR-DC-15). It is implemented as code under
`core/extractors/` and **invoked** by this skill — it is *not* steps you perform by reasoning. Running the
code is what makes "deterministic, model-free" real and repeatable; do not re-derive these steps in prose.

```
dispatch(repo) -> code_map.json:                      # TECH_SPEC §5.5
  L = detect_language(repo)                            # core.extractors.detect_language — DETERMINISTIC
  E = extractor_for(L)                                 # core.extractors.extractor_for  — registry lookup
  if E:
      raw     = E(repo)                                # frozen tool (tree-sitter-c for C; TASK-009)
      entries = normalize(raw)                         # → §3.3 file-entry shape (structural fields only)
      cov     = "coarse"                               # per D6a; deep pass confirms
  else:
      entries = model_fallback(repo)                   # TASK-010 — model derives structure, lower-coverage
      mark_all(entries, coverage="coarse"); force_top_level_coverage("coarse")
  for e in entries:
      e.purpose, e.tags = model_enrich(e)              # TASK-011 — MODEL owns purpose + tags ONLY
      assert e.tags ⊆ domain_vocabulary                # TASK-011 — D5 / §10
  edges = merge_edges(entries)                         # core.extractors.merge_edges — DETERMINISTIC closure
  return assemble(entries, edges, coverage_report)
```

### Division of labor (fixed — never blur)

| Step | Owner | Where | Determinism |
|---|---|---|---|
| `detect_language` | **code** | `core/extractors/__init__.py` | deterministic (FR-DC-15) |
| `extractor_for` (registry) | **code** | `core/extractors/__init__.py` | deterministic |
| structural fields (`path/module/interfaces/depends_on/used_by`) | **extractor** | `core/extractors/<lang>_extractor.py` | deterministic (frozen) |
| `normalize` (→ §3.3 shape) | **code** | `core/extractors/__init__.py` | deterministic |
| `merge_edges` (`depends_on ↔ used_by`) | **code** | `core/extractors/__init__.py` | deterministic |
| `purpose` + `tags` | **model** | `model_enrich` (TASK-011) | the one model-driven step |
| structure when no extractor exists | **model** | `model_fallback` (TASK-010), forced `coverage: coarse` | escape hatch, flagged |

The model is in the loop for **meaning only** (`purpose`/`tags`, and — flagged as coarse — fallback
structure). It is never the source of detection, normalization, edges, or the gate decision.

### Language detection (deterministic — FR-DC-15)

`detect_language(repo)` is a file-glob histogram over source-file extensions, with build-manifest
filenames (`Makefile`, `CMakeLists.txt`, `pom.xml`, …) used only to break ties; vendored/build dirs are
pruned. Same tree in → same language out. Slice 1 returns a single dominant language (single-repo,
single-language MVP scope); polyglot per-subtree routing is Phase 5. `fixtures/c_repo/` detects as `c`.

### Normalization contract (the language seam — §5.5)

Every extractor — deterministic or fallback — MUST emit file entries that `normalize()` maps to the §3.3
file-entry shape: `path, module, interfaces[], depends_on[], used_by[], coverage`. `normalize()` seeds
`purpose`/`tags` **empty** (the model fills them in TASK-011) and emits the reserved `external_calls`/
`exposes` empty (FR-DC-13). The extractor owns the structural fields; the model is **not** the primary
source of dependency edges. Adding a language = "write one more extractor + `register_extractor(L, …)`";
nothing else changes.

### Extractor slots (registry)

- **C** → `core/extractors/c_extractor.py` (TASK-009), registered via `register_extractor("c", …)`.
  Until registered, `extractor_for("c")` returns `None` and a C repo routes to the fallback.
- **Model-only fallback** → the `else` branch (TASK-010): reached only when `extractor_for(L)` is `None`;
  marks every entry `coverage: coarse` and forces top-level coverage coarse.

### Gate (forward reference)

The 3-branch onboarding/cache gate (onboard / reuse-cached / rebuild-changed-files) wraps this dispatch
and is **fully deterministic** (no model in the branch decision). It is built in TASK-013 (§5.3) on top of
these same `detect_language` / `extractor_for` primitives.

---

## Output — `context_set/code_map.json` (§3.3)

For each module/file (structural fields from the extractor; `purpose`/`tags` from the model in TASK-011):
```json
{
  "path": "src/routing/brand_router.c",
  "module": "routing",
  "purpose": "Routes a transaction to the correct card-brand handler",
  "interfaces": ["route_transaction(txn)", "register_brand(brand)"],
  "depends_on": ["settlement/reconciler", "config/brand_rules"],
  "used_by": ["api/transaction_controller"],
  "tags": ["routing", "card_brand"],
  "coverage": "coarse",
  "external_calls": [],
  "exposes": []
}
```
Plus a top-level coarse component overview (module → one-line purpose) and the extractor's
`coverage_report` (emitted every build — §5.4).

The `tags` must be drawn only from the **domain vocabulary** (D5 / §10) and align with the **profile
topics** used by BRD/FRD routing, so the code sections can find the right map entries
(adapter-emits ↔ profile-topics contract).

## Rules

- Map, don't copy — never inline large code bodies into `code_map.json`; reference by `path`.
- Capture both directions of dependency (`depends_on` and `used_by`) where discoverable — the impact
  assessment needs the closure (resolved by `merge_edges`, not by hand).
- Be honest about coverage: static-analysis blind spots (function pointers, macros, `#ifdef`,
  config-driven wiring) are marked `coverage: coarse` with `unresolved_patterns` and confirmed in the deep pass.

## Boundaries

- Does not assess impact (no requirement is involved here) — that is `code_impact`, Phase B.
- Does not read or summarize every file exhaustively.
- Does not modify `repo/`, and does not generate or modify the **frozen** extractor (`core/extractors/`).
