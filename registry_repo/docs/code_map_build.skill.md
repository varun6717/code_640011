---
name: code_map_build
type: Pre-processing skill (Bitbucket domain adapter, Phase A)
layer: Data & context
consumes: repo/ (cloned Bitbucket repo)
produces: context_set/code_map.json
runs: once per repo · requirement-independent · cached
---

# Code Map Build

## Role

You build a **coarse, navigable index** of an already-cloned codebase. Code is handled differently from
documents: the full repo lives on disk in `repo/` and is read natively on demand — you do **not**
summarize all the code. You produce a lightweight `code_map.json` that lets later steps (coarse impact,
deep impact) find and pull the right files.

Ingestion (the `git clone` into `repo/`) is done by a script before you run. Your job is the map.

## Principle — coarse-first, deep-on-demand, language-agnostic

Do **not** read every file. Build a module/file-level map; fine (function-level) detail is read later,
on demand, only for the slice an impact assessment points at.
- **Language-agnostic.** Works for any language. Derive structure and dependency edges from whatever that
  language uses to declare and connect modules — `import` (Python/Java/JS/Go), `#include` + headers
  (C/C++), `require`/`use` (Ruby/Rust), package/namespace declarations, build manifests. The example
  below is illustrative, not language-specific.
- Start from the **file tree** and **entry points** (cheap) to establish module structure.
- **Prefer deterministic tooling on large repos.** Use language-appropriate tools to extract structure
  and edges mechanically and cheaply — file-tree listing, a grep/parse pass over the language's
  import/include statements, and symbol/cross-reference tools (e.g. `tree-sitter` for C per ADR-001, a
  language server, or a dependency-graph tool). Reserve the model for the `purpose`/`tags` summarization it is
  actually good at. The per-language extractor is **onboarded once and frozen** (human-gated); this skill
  **consumes** it and does **not** generate or modify it at map-build runtime (see FR-DC-14…17). When no
  frozen extractor exists for a language, fall back to model-derived structure and mark it lower-coverage.
- **Bound context — never load the whole repo.** Summarize per file/module in bounded, parallel units
  (the ingestion fan-out: each unit its own context window, results merged) or let tooling carry the
  structural bulk. Context is bounded by the unit, not the repo; concurrency/batch size is an
  orchestration setting, not fixed here.
- Summarize at **module/file** granularity and capture **dependency edges** — they're what make this an
  *impact* map rather than a flat summary. Edge resolution — matching one file's outbound references to
  another's exposed interfaces — is a deterministic **merge step** over the collected entries, not
  something a single file's context can do alone.

## Output — `context_set/code_map.json`

For each module/file:
```json
{
  "path": "src/routing/brand_router.java",
  "module": "routing",
  "purpose": "Routes a transaction to the correct card-brand handler",
  "interfaces": ["routeTransaction(txn)", "registerBrand(brand)"],
  "depends_on": ["settlement/reconciler", "config/brand_rules"],
  "used_by": ["api/transaction_controller"],
  "tags": ["routing", "card_brand"]
}
```
Plus a top-level coarse component overview (module → one-line purpose).

The `tags` must align with the **profile topics** used by the BRD/FRD routing, so the code sections can
find the right map entries (adapter-emits ↔ profile-topics contract).

## Rules

- Map, don't copy — never inline large code bodies into `code_map.json`; reference by `path`.
- Capture both directions of dependency (`depends_on` and `used_by`) where discoverable — the impact
  assessment needs the closure.
- Be honest about coverage: if a module wasn't deeply explored, mark it coarse so deep impact knows to drill.

## Boundaries

- Does not assess impact (no requirement is involved here) — that is `code_impact`, Phase B.
- Does not read or summarize every file exhaustively.
- Does not modify `repo/`.
