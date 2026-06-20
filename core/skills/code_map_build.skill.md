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
dispatch(repo) -> code_map.json:                      # TECH_SPEC §5.5, revised by ADR-002
  partitions = partition_by_language(repo)             # core.extractors — DETERMINISTIC {lang: [files]}
  entries = []
  for lang, files in partitions:
      E = extractor_for(lang)                          # core.extractors.extractor_for — registry lookup
      if E:
          entries += normalize(E(files))               # frozen tool (tree-sitter-c for C; TASK-009)
      else:
          entries += model_fallback(files)             # TASK-010 — model derives structure for a partition
                                                        #   with no extractor; mark_all coverage="coarse";
                                                        #   these files are files_fallback (never dropped)
  vocab = load_domain_vocabulary(domain)               # core.extractors — D5-pinned set (§10)
  for e in entries:
      purpose, tags = model_enrich(e)                  # TASK-011 — MODEL owns purpose + tags ONLY
      apply_enrichment(e, purpose, tags)               # core.extractors — writes ONLY purpose+tags (guard)
  assert_tags_in_vocabulary(entries, vocab)            # core.extractors — DETERMINISTIC gate; D5 / §10
  edges = merge_edges(entries)                         # core.extractors.merge_edges — DETERMINISTIC closure
  return assemble(entries, edges, coverage_report)     # files_seen = ALL source files; residue = files_fallback;
                                                        #   coverage = files_extracted / files_seen (§5.4 / ADR-002).
                                                        #   Force top-level coverage="coarse" ONLY if the WHOLE
                                                        #   repo fell back (files_extracted == 0); else report
                                                        #   the computed ratio (§5.5).
```

**Polyglot dispatch (ADR-002).** A repo is partitioned by language; the **majority language goes through
its frozen extractor**, the **residue goes through the model fallback** (marked coarse), and both merge into
one `code_map.json`. No file is dropped. Because residue counts as `files_fallback`, a genuinely bilingual
repo's coverage drops below the floor → `REONBOARD_FLAG` names the un-onboarded language; a few ancillary
scripts barely move coverage and raise nothing. `detect_language` is still used for the single **dominant**
language (top-level `code_map.language`, gate/cache key).

### Division of labor (fixed — never blur)

| Step | Owner | Where | Determinism |
|---|---|---|---|
| `detect_language` / `partition_by_language` | **code** | `core/extractors/__init__.py` | deterministic (FR-DC-15) |
| `extractor_for` (registry) | **code** | `core/extractors/__init__.py` | deterministic |
| structural fields (`path/module/interfaces/depends_on/used_by`) | **extractor** | `core/extractors/<lang>_extractor.py` | deterministic (frozen) |
| `normalize` (→ §3.3 shape) | **code** | `core/extractors/__init__.py` | deterministic |
| `merge_edges` (`depends_on ↔ used_by`) | **code** | `core/extractors/__init__.py` | deterministic |
| `purpose` + `tags` | **model** | `model_enrich` (TASK-011) | the one model-driven step |
| structure when no extractor exists | **model** | `model_fallback` (TASK-010), forced `coverage: coarse` | escape hatch, flagged |

The model is in the loop for **meaning only** (`purpose`/`tags`, and — flagged as coarse — fallback
structure). It is never the source of detection, normalization, edges, or the gate decision.

### Language detection + partition (deterministic — FR-DC-15)

`detect_language(repo)` is a file-glob histogram over source-file extensions, with build-manifest
filenames (`Makefile`, `CMakeLists.txt`, `pom.xml`, …) used only to break ties; vendored/build dirs are
pruned. Same tree in → same dominant language out. It feeds the top-level `code_map.language` and the gate.
`partition_by_language(repo)` (ADR-002) returns the full `{lang: [files]}` map over the same deterministic
extension signals, so a polyglot repo routes each language independently (above). `fixtures/c_repo/`
detects as `c`; `fixtures/mixed_repo/` partitions into `c` (majority) + residue. Per-*subtree* language
nesting and multi-*repo* breadth remain Phase 5.

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
- **Model-only fallback** → the `else` branch (TASK-010): reached for any partition whose language has no
  registered extractor — whether that is the whole repo (no extractor for the dominant language) or just
  the **residue** of a polyglot repo (ADR-002). Operates over a **file set**; marks every entry
  `coverage: coarse`; residue files count as `files_fallback` in the `coverage_report`.

### Model fallback — the model-driven escape hatch (TASK-010)

`model_fallback(files)` is the **one structural step the model performs**, and the only one. The frozen
extractors are deterministic Python (`tree-sitter` for C); this branch exists for the case where there is
**no frozen extractor to run** — so nothing deterministic *can* run, and the model is the only thing that
can derive structure from the source. It is the **safety net** (§5.7): when a language is un-onboarded (or
its toolchain is absent and unprovisionable), correctness degrades to **coarse coverage, never a hard
failure**. It is not a per-domain branch — ingestion never forks on domain (D7); it forks only on
"is there a registered extractor for this language?".

**When it runs.** Exactly the partitions where `extractor_for(lang)` is `None` (FR-DC-17) — no guess, no
heuristic. Two shapes, *one* function (ADR-002 — this is the §5.5 fallback at finer granularity, additive,
not new):
- **Whole repo** — no extractor for the dominant language → every file is a fallback file.
- **Residue** — a polyglot repo whose majority language has a frozen extractor; the leftover non-majority
  files route here while the majority goes through its extractor. Both halves merge into one `code_map.json`.

**Input.** A **file set** (the repo-relative paths of that partition) — *not* a self-glob of the repo, *not*
the whole tree. You read those files (bounded, on demand) and derive structure for them only.

**What the model derives — structural fields only, same §3.3 contract as a frozen extractor.** For each
file: `path`, `module`, `interfaces[]`, `depends_on[]` (best-effort from imports/calls you can see). Leave
`used_by` to the deterministic `merge_edges` closure, and leave `purpose`/`tags` to `model_enrich` — the
fallback does **not** pre-empt them; its entries flow through the *same* shared
`normalize → model_enrich → merge_edges` path as extractor entries, so the rest of the pipeline cannot tell
the two sources apart. The model is the *origin of structure* here, but it is still **never** the source of
the detection, the normalization, the edge closure, or the gate decision.

**Coarse, unconditionally.** Mark **every** fallback entry `coverage: "coarse"`. Model-derived structure is
never promoted to `deep` — only the Stage-2 deep pass (`code_impact`) ever does that, and only on real code.

**Coverage accounting (§5.4 — the honesty mechanism).** Fallback files count as `files_fallback`, **never**
`files_extracted`. `files_seen` counts *all* source files across every partition. So
`coverage = files_extracted / files_seen` **drops in exact proportion to the residue** — the deterministic
share. This self-tunes the only real ambiguity (ancillary scripts vs. a genuine second language): a few
build scripts barely move coverage and raise nothing; a genuine ~50/50 second language pushes coverage
below the **0.80 floor**, and `check_coverage` raises a `REONBOARD_FLAG` naming the un-onboarded
language(s) (§5.4) — a human-decided "should we onboard an extractor for this?", recorded in
`decisions.jsonl`. The fallback **raises its hand; it never auto-onboards or rewrites a frozen extractor.**

**Top-level coverage — force vs. compute.** Force the top-level `coverage` to `"coarse"` **only when the
whole repo went to fallback** (no deterministic share exists at all). When an extractor handled the majority
and only the residue fell back, do **not** force it: report the computed `files_extracted / files_seen`
ratio — the number itself already carries the degraded signal, and forcing would hide how much *was*
deterministically covered.

**Worked examples.**
- `fixtures/mixed_repo/` — `detect_language` = `c`; partitions `c` (4 files → frozen extractor) + residue
  `java` (1) + `python` (1) → fallback, both coarse. `files_seen = 6`, `files_fallback = 2`;
  `coverage ≈ 4/6 = 0.67 < 0.80` → `REONBOARD_FLAG(java, python)`. Top-level coverage is the **computed**
  0.67 (an extractor covered the majority), not force-set.
- A fully non-C / un-onboarded repo — *every* file routes to fallback; `files_extracted = 0` →
  `coverage = 0` → below floor, and the top-level coverage is **force-set** `"coarse"` (whole repo fell back).

### Model enrichment — `purpose` + `tags`, and only those (TASK-011)

After every partition has been normalized (extractor entries + any fallback entries, all in the §3.3
shape with `purpose`/`tags` seeded empty), the **one model-driven enrichment step** runs over the merged
entry list. It is the model's *only* contribution to a normal (extractor-covered) map, and it is bounded
to **meaning**:

- **What the model sets — exactly two fields.** For each entry the model returns a one-line `purpose`
  (what the file does, in business-legible terms) and a `tags[]` list. It reads the entry's structural
  fields and may selectively open the file it names (bounded, on demand) to judge purpose/tags — it does
  **not** re-derive structure. `model_enrich(e)` is performed by *you* (the agent), by reasoning; there is
  deliberately no Python function for it.
- **The write-guard.** Write the result back only through `apply_enrichment(e, purpose, tags)`
  (`core.extractors`). That setter touches `purpose` and `tags` and **nothing else** — it cannot reach
  `path/module/interfaces/depends_on/used_by/coverage` or the reserved `external_calls`/`exposes`. So even
  if a model turn "helpfully" proposes an edge or renames a module, that edit has no path into the map: the
  structural fields stay exactly as the deterministic extractor (or `merge_edges`) produced them
  (FR-DC-17). The model is in the loop for meaning only — never detection, normalization, edges, or the gate.
- **`tags ⊆ vocabulary`, asserted in code.** Tags are drawn **only** from the domain vocabulary
  (D5 / §10), loaded by `load_domain_vocabulary(domain)`. After enrichment, `assert_tags_in_vocabulary(
  entries, vocab)` is the hard gate: it raises `VocabularyError` naming every offending `(path, tag)` pair,
  failing the build loudly (FR-DC-09) rather than leaking a junk tag that would silently mis-route a BRD/FRD
  section. In practice `code_map_build` emits only the six **code tags** D5 flags `Code tag? = yes`
  (`card_brand, routing, message_format, settlement, transaction_flow, error_handling` — the `CODE_MAP_TAGS`
  subset, matching `adapter.yaml`'s `code_pipeline` emits); the gate enforces containment in the full
  vocabulary, so a non-code tag is not *rejected* but an out-of-vocabulary string is. A file the model finds
  no in-vocabulary tag for keeps `tags: []` (e.g. a shared utility header or the vendor shim) — empty is
  honest, an invented tag is not.

> **Vocabulary source (TASK-011 stub note).** The canonical vocabulary is
> `core/profiles/payment_brand/vocabulary.payment_brand.yaml` (authored in TASK-014). Until that file
> exists, `load_domain_vocabulary` returns the **D5-pinned stub** — the same 12 tags, reproduced from the
> frozen D5 table, not invented. TASK-021/046 (`check_vocab_containment.py`) re-points the check at the YAML
> file. The assertion behaviour does not change; only the source of the set moves from constant to file.

**Edges stay deterministic.** `model_enrich` never sets `depends_on`/`used_by`. The closure is the
deterministic `merge_edges(entries)` step that runs *after* enrichment (it does not depend on `purpose`/
`tags`), matching each entry's outbound `depends_on` to another entry's identity and back-filling `used_by`.
This is why the C extractor leaves `used_by` empty (TASK-009) — the merge owns it, not the extractor and
not the model.

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
