# TASK_LIST — PDLC_App_v2 Build (external Claude Code)

**Project:** PDLC_App_v2 · JPMC Merchant Services · AI Automation
**This artifact:** the Claude Code-executable build sequence for the **external build** (validated here, ported to VDI later).
**Authoritative design:** `docs/REQUIREMENTS.md` (WHAT/WHY, D1–D10) ▸ `docs/TECH_SPEC.md` (HOW, normative schemas) ▸ supporting docs in `docs/`.
**Read `CLAUDE.md` first.** It carries the doc precedence, the hard rules, and the context-restart protocol.

**First slice:** single domain `payment_brand`; single repo; **BRD → FRD only** (no Jira); one PDF + one Stratus C repo. Breadth is Phase 5 (named, not built).

---

## How to read a task

Every task is sized for **one Claude Code session** and carries:

- **Depends on** — prior tasks + on-disk artifacts that must already exist. Verify them before starting.
- **Reads** — the exact `docs/<FILE>` § to open. **Open and read those sections before writing.** The cited block is the contract; do not work from memory.
- **Creates / edits** — exact output paths (from `docs/TECH_SPEC.md` §2).
- **Acceptance** — checkable conditions; the task is done only when all hold.
- **Fixture / proof** — what demonstrates correctness.
- **Satisfies** — the FR-ID(s).
- **Model** — suggested Claude model. `Sonnet` = default for all tasks; `Opus` = tasks where a design mistake propagates far or the logic is deeply layered.

Tick the checkbox in the index below when a task is done, then commit. A fresh session resumes at the first unchecked box.

## Context-restart protocol

Context will get large. **You may start a fresh chat at any 🔁 phase boundary.** To resume: read `CLAUDE.md` → find the first unchecked task below → confirm against disk (`core/`, `overlays/`, `fixtures/`, `runs/`) → execute. State lives in files and git, never in the conversation.

## Citation key

`docs/REQUIREMENTS.md` is cited by **decision (D1–D10)** and **FR-ID**. `docs/TECH_SPEC.md` is cited by **section (§N.N)**. When a task says *Reads: `docs/TECH_SPEC.md` §3.3*, open that exact section and conform to its YAML/JSON block field-for-field.

---

## Progress index (tick as you go)

> **Model key — copy any line into a new session and ask "explain this task and confirm the model":**
> `Sonnet` = default for all tasks · `Opus` = deep design artifact or mistake propagates far

**Setup**
- [x] TASK-000 — Repo scaffold: directory tree, .gitkeeps, initial git commit · `Sonnet`

**Phase 0 — UI / input-contract design (in CHAT as `.jsx`, not Claude Code)**
- [x] TASK-001 — UI pattern library: locked interaction patterns every screen composes from (chat/JSX only) · `N/A`
- [x] TASK-002 — UI screens → locked `UI_INPUT.yaml` contract (chat/JSX only) · `N/A`

**Phase 1 — Pre-tasks**
- [x] TASK-003 — PDF fixtures: 2× Mastercard mandate PDFs + `expected_manifest_entries.json` oracle for TASK-034 · `Sonnet`
- [x] TASK-004 — Synthetic Stratus C repo: payment routing code with function-pointer dispatch, macros, `#ifdef` patterns the extractor must handle · `Sonnet`
- [x] TASK-005 — Hand-author `expected_code_map.json` against C fixtures; human-signed-off oracle that grades TASK-012 · `Sonnet`
- [x] TASK-006 — Check C extractor tooling (`tree-sitter`/`tree-sitter-c` per ADR-001); write `ENV_PRECHECK.md` with version or fallback decision · `Sonnet`
- [x] TASK-007 — Record Copilot/VDI PASSED 2026-06-16 note in `ENV_PRECHECK.md` (no re-run needed) · `Sonnet`
- [x] TASK-008 — Language detection + partition + dispatcher skeleton in `code_map_build.skill.md`; normalization contract maps any extractor output to §3.3 shape (per-language partition dispatch per ADR-002) · `Sonnet`
- [x] TASK-009 — C extractor: `tree-sitter` (ADR-001) over the C partition → structural fields only; mark function-pointer/macro/`#ifdef` blindspots as `coverage: coarse` · `Sonnet`
- [x] TASK-010 — Model fallback over a file set (whole-repo + polyglot residue, ADR-002): derive structure via model, mark entries `coverage: coarse`, residue → `files_fallback` · `Sonnet`
- [x] TASK-011 — Model enrichment: model sets `purpose`+`tags` only; deterministic `merge_edges`; assert `tags ⊆ vocabulary` · `Sonnet`
- [x] TASK-012 — Validate extractor output vs signed-off oracle; meet coverage floor 0.80; human-gate freeze; write `onboarding_manifest.yaml` (incl. reserved `vocab_sha`/`adequacy_threshold`, ADR-003) · `Sonnet`
- [x] TASK-013 — 3-branch gate (fully model-free): onboard / reuse-cached / rebuild-changed-files; `REONBOARD_FLAG` if below floor; **+ L1 vocabulary-adequacy detector** (`uncovered_concepts` recurrence + `untagged_ratio` floor → `VOCAB_GAP_FLAG`, ADR-003) + `vocab_sha` cache key · `Sonnet`
- [x] TASK-014 — Transcribe D5 vocabulary table verbatim into `vocabulary.payment_brand.yaml` (12 tags, emitted-by mapping) · `Sonnet`
- [x] TASK-015 — Author `brd_profile.payment_brand.yaml`: `must_capture` + `probe_if_missing` per topic per section; foundation every BRD run depends on · `Opus`
- [x] TASK-016 — Author `frd_profile.payment_brand.yaml`: same shape + `functional_kind` + `traces_to` resolving to real BRD anchors · `Opus`
- [x] TASK-017 — `adapter.yaml` pack manifest + `pdf_extract` skill; F1 (+3) emit-map drifts reconciled w/ V (see CLAUDE.md) · `Sonnet`
- [x] TASK-018 — `article_summarize` skill: emits `brand_rules`, `message_format`, `interchange_fees`, `reporting` (reconcile F1) · `Sonnet`
- [x] TASK-019 — `change_type_assess` skill: emits `mandate`, `card_brand`, `routing`, `certification`, `compliance_deadline` (reconcile F1) · `Sonnet`
- [x] TASK-020 — Two generic source-type-keyed connectors: `clone.py` (Bitbucket) + `ingest_file.py` (direct-file PDF; SharePoint deferred P5) · `Sonnet`
- [x] TASK-021 — Verify §10.3/10.4/10.5 domain-seam build checks all green; F1 reconciled before proceeding · `Sonnet`

**Phase 2 — Core scaffold & runtime-tool seam**
- [x] TASK-022 — Run-workspace template under `runs/_template/` + JSON-schema validators for 3 ledger files · `Sonnet`
- [x] TASK-023 — `merge_manifest.py`: deterministic fan-in of per-source slices → `index.json`; failed sources marked, never dropped · `Sonnet`
- [x] TASK-024 — `hydrate.py`: `git clone` + checkout `registry_sha` + selective copy of `core/`+`profiles/`+`overlays/` into run scaffold · `Sonnet`
- [x] TASK-025 — Transcribe D9 block into `overlay_manifest.yaml`: 8 roles, 3 prompt files, per-tool launch · `Sonnet`
- [x] TASK-026 — One canonical `instruction_file.template.md`; generation emits `CLAUDE.md` or `copilot-instructions.md` by `runtime_tool` · `Sonnet`
- [x] TASK-027 — Claude overlay: 8 thin `.md` agent wrappers, each body pointing at one shared `core/skills/` skill · `Sonnet`
- [x] TASK-028 — Claude overlay: 3 prompt files (`start-brd/frd/jira`) + `terminal_interactive` launch · `Sonnet`
- [x] TASK-029 — Copilot overlay: parity twin of TASK-027 in native Copilot syntax (frontmatter + location differ) · `Sonnet`
- [x] TASK-030 — Copilot overlay: parity twin of TASK-028 with `agent_mode` launch + `Ctrl+N` gesture · `Sonnet`
- [x] TASK-031 — `generate.py` scaffolder: deterministic Generate → run workspace + instruction file + G0 inspection checkpoint · `Opus`
- [x] TASK-032 — `telemetry.py`: `emit()` + `decisions.jsonl` writer + `run_state.json` updater covering all §8.1 events · `Sonnet`

**Phase 3 — Framework build: the spine**
- [x] TASK-033 — `source_processor` skill: fan-out worker per source; failure-isolated; reads `adapter.yaml` for run order; no domain knowledge · `Opus`
- [x] TASK-034 — Run `pdf_extract`→`article_summarize`→`change_type_assess` over PDF fixtures; verify entries vs `expected_manifest_entries.json` · `Sonnet`
- [x] TASK-035 — Clone SEAL-ID repo + run `merge_manifest.py` → assembled `index.json` with `sources_status` · `Sonnet`
- [x] TASK-036 — `code_map_build` skill: drive frozen extractor through 3-branch gate → `code_map.json` per §3.3 · `Sonnet`
- [x] TASK-037 — `brd_author`: deterministic baseline+profile merge + discovery framing (2–3 questions, seed coarse code pass) · `Opus`
- [x] TASK-038 — `brd_author`: per-section authoring loop; §3.2 selective-read routing; `must_capture` check; probe gaps; coverage footer · `Opus`
- [x] TASK-039 — `brd_author`: cite-or-flag grounding rules; revisit/shared-memory (never re-ask answered questions) · `Sonnet`
- [x] TASK-040 — `code_impact` coarse pass: map-only, no source files; match requirement topics × `code_map` tags → ranked candidate areas · `Sonnet`
- [x] TASK-041 — `code_impact` deep pass: selective-read flagged slice from `repo/`; trace real closure; emit Flags schema every run · `Opus`
- [x] TASK-042 — `brd_author` flag loop: surface→wait→apply→conditional re-run; material vs advisory per D6c; no auto scope changes · `Opus`
- [x] TASK-043 — `brd_validator` + G1: score = 0.7×topic_coverage + 0.3×citation_integrity; hard preconditions on required topics + flags · `Sonnet`
- [x] TASK-044 — `frd_author` skill: consume accepted BRD; `traces_to`; carry file/function detail forward that BRD stays silent on · `Opus`
- [x] TASK-045 — `frd_validator` + G2: score = 0.5×traceability + 0.5×testability; hard precondition every BRD requirement traced · `Sonnet`

**Phase 4 — Build harness & acceptance**
- [x] TASK-046 — `check_vocab_containment.py`: assert all profile topics + adapter tags ∈ `vocabulary.payment_brand.yaml` · `Sonnet`
- [x] TASK-047 — `check_overlay_parity.py`: both overlays expose all 8 manifest roles pointing at same shared skills · `Sonnet`
- [x] TASK-048 — `build_checks.py` runner (all five checks) + `metrics_scan.py` deriving all MVP metrics from `telemetry.jsonl` · `Sonnet`
- [x] TASK-049 — End-to-end acceptance: PDF + repo → BRD vN → FRD; flag loop + G1 reopen; `build_checks.py` green · `Opus`

**Phase 5 · Milestone 5A — Self-serve run: UI + hosted sources + live connectors** *(PRIORITY)*
- [x] TASK-050 — Generate backend service (FastAPI): config → `UI_INPUT.yaml` → `generate.py` (G0); status from ledger · `Sonnet`
- [ ] TASK-051 — React Run Configurator from `PDLC_Configurator.jsx` (5 tabs) → emits §3.1 `UI_INPUT.yaml`; Generate + hand-off · `Sonnet`
- [ ] TASK-052 — `jpmc_adapters/auth.py` real `resolve_auth` (auth_ref → secret store; bitbucket/sharepoint) · `Sonnet`
- [ ] TASK-053 — Registry (repo #1) on Bitbucket + hydrate-from-remote at pinned `registry_sha` · `Sonnet`
- [ ] TASK-054 — Live Bitbucket code-source clone (repo #2) through the resolved auth seam; pin `commit_sha` · `Sonnet`
- [ ] TASK-055 — `ingest_sharepoint.py` — SharePoint PDF connector (source-type-keyed; same descriptor) · `Sonnet`
- [ ] TASK-056 — Self-serve acceptance: UI → Generate → VS Code Claude Code/Copilot → BRD/FRD · `Opus`

**Phase 5 · Milestone 5B — Enhancements (backlog; see end of file)**

---

# Setup

### TASK-000 — Repository scaffold + docs + CLAUDE.md
- **Phase:** Setup · **Depends on:** none
- **Model:** Sonnet — mechanical directory creation and git init; no design decisions (this is first). On disk to start: `CLAUDE.md`, `TASK_LIST.md`, `docs/` already present (from the starter zip).
- **Reads:** `docs/TECH_SPEC.md` §2.1 (registry layout) and §2.2 (run-workspace layout) — the exact directory tree; `docs/TECH_SPEC.md` Appendix B (hydration — for context only; the external repo *is* the working tree, so no registry clone is performed here).
- **Creates / edits:** the on-disk skeleton —
  ```
  core/skills/                      core/scripts/
  core/extractors/                  core/adapters/jpmc_adapters/
  core/profiles/payment_brand/adapter/
  core/templates/payment_brand/
  overlays/claude/.claude/agents/   overlays/claude/prompts/
  overlays/copilot/                 overlays/copilot/prompts/
  fixtures/pdf/                     fixtures/c_repo/
  runs/                             (run workspaces land here in Phase 3+)
  ```
  Place a `.gitkeep` in each leaf dir. Confirm `CLAUDE.md`, `TASK_LIST.md`, and `docs/` are at root. `git init` and make the first commit.
- **Do:** Create exactly the directory tree above (it mirrors `docs/TECH_SPEC.md` §2.1 minus the `registry/` wrapper — in the external build the repo root is the registry working tree, so `core/` and `overlays/` sit at root). Do not create files the later tasks own; only the empty tree + `.gitkeep`s.
- **Acceptance:**
  - The tree matches §2.1 (every `core/…` and `overlays/…` leaf present) plus `fixtures/` and `runs/`.
  - `CLAUDE.md`, `TASK_LIST.md`, `docs/` present at root; `docs/` contains REQUIREMENTS.md, TECH_SPEC.md, SKILLS_INDEX.md, BUILD_OVERVIEW.md, COPILOT_VDI_VALIDATION.md, brd_frd_overview.html, and the four seed `.skill.md` files.
  - `git status` is clean after the initial commit; `.gitkeep`s are tracked.
- **Fixture / proof:** a directory listing diffed against §2.1.
- **Satisfies:** FR-XS-05 (durable file layout).

> 🔁 **Phase 0 runs in chat, not Claude Code.** If you are in Claude Code, skip to TASK-003; do Phase 0 in the Claude.ai chat interface. A fresh context is fine before Phase 1.

---

# Phase 0 — UI / input-contract design  *(in the Claude.ai chat as `.jsx` artifacts — NOT a Claude Code build phase)*

The UI **collects configuration only** and **is** the visible `UI_INPUT.yaml` contract (`docs/TECH_SPEC.md` §3.1, FR-XS-02). No plumbing, no judgment (FR-XS-03). Pattern-first, then screens. For the first slice the inputs are pre-defined (the PDF + the Stratus repo by SEAL ID).

### TASK-001 — UI pattern library
- **Phase:** P0 (chat/`.jsx`) · **Depends on:** none.
- **Reads:** `docs/TECH_SPEC.md` §3.1 (`UI_INPUT.yaml` field set); `docs/REQUIREMENTS.md` FR-XS-02, FR-XS-22 (start-gesture surfacing); `docs/BUILD_OVERVIEW.md` §5 (UI collects: working path, sources+URLs, frame, domain, runtime tool).
- **Creates / edits:** `.jsx` pattern artifacts in the chat (design phase — no repo paths).
- **Do:** Build the locked interaction patterns (field, source-row, validation, review/Generate, start-gesture surface) that every screen composes from.
- **Acceptance:** every `UI_INPUT.yaml` field in §3.1 maps to exactly one pattern; no pattern implies plumbing or judgment; the per-tool start gesture (FR-XS-22) has a surface.
- **Fixture / proof:** a walkthrough emitting the slice-1 `UI_INPUT.yaml` (PDF + Bitbucket `SEAL-12345`) byte-for-byte against §3.1.
- **Satisfies:** FR-XS-02, FR-XS-03, FR-XS-22.

### TASK-002 — UI screens → locked `UI_INPUT.yaml`
- **Phase:** P0 (chat/`.jsx`) · **Depends on:** TASK-001.
- **Reads:** `docs/TECH_SPEC.md` §3.1; `docs/REQUIREMENTS.md` FR-XS-09 (two-step Generate), FR-XS-16 (immutable post-Generate), FR-XS-10 (`registry_sha` pin), NFR-01.
- **Creates / edits:** `.jsx` screen artifacts + a **locked `UI_INPUT.yaml` example** (used as the contract by TASK-031's scaffolder).
- **Do:** Compose patterns into the config screens; lock the exact `UI_INPUT.yaml` they emit.
- **Acceptance:** screens emit *only* `UI_INPUT.yaml`; `auth_ref` points at the seam with no secret on screen (NFR-01); re-config is a **new run** (new `run_id`), never in-place (FR-XS-16); two-step Generate-then-Run visible (FR-XS-09).
- **Fixture / proof:** the locked example round-trips back into the screens unchanged.
- **Satisfies:** FR-XS-02, FR-XS-09, FR-XS-10, FR-XS-16, NFR-01.

> The FastAPI/React app that *implements* Generate is Phase 5. P0 locks the contract; TASK-031 lays a deterministic slice-1 scaffolder that consumes it.

> 🔁 **Fresh-context safe before Phase 1.**

---

# Phase 1 — Pre-tasks

Order: fixtures → env/tooling → extractor onboarding → domain seam. The extractor must be **frozen** before the spine can build a `code_map`; the domain seam must exist before the framework can run.

## Bucket 1 — Input fixtures

### TASK-003 — PDF input fixture(s)
- **Phase:** P1 · **Depends on:** none.
- **Model:** Sonnet — synthetic PDF content generation; no deep reasoning needed
- **Reads:** `docs/REQUIREMENTS.md` D5 (the 12-tag vocabulary table — which tags the doc pipeline must be able to surface); `docs/TECH_SPEC.md` §3.2 (`index.json` provenance + `topics`).
- **Creates / edits:** `fixtures/pdf/<name>.pdf` + `fixtures/pdf/expected_manifest_entries.json`.
- **Do:** Produce representative Payment Brand PDF(s) (a mandate/spec article) plus the expected `index.json` entries (topics + descriptor) each should yield.
- **Acceptance:** content exercises the doc-emitted tags (`mandate`, `brand_rules`, `message_format`, `interchange_fees`, `reporting`, `card_brand`, `routing`, `certification`, `compliance_deadline`); ≥1 PDF carries a mandate ID + compliance deadline.
- **Fixture / proof:** this task *is* the fixture; `expected_manifest_entries.json` grades TASK-034.
- **Satisfies:** FR-DC-03, FR-DC-04.

### TASK-004 — Stratus C-pattern catalog → `.c`/`.h` fixtures
- **Phase:** P1 · **Depends on:** none.
- **Model:** Sonnet — writing realistic C code with specific structural patterns; no deep design decisions
- **Reads:** `docs/TECH_SPEC.md` §3.3 (`code_map.json` file-entry schema); §5.5 (normalization contract — what the extractor must emit).
- **Creates / edits:** `fixtures/c_repo/**` (`.c`/`.h` tree) + `fixtures/c_repo/PATTERN_CATALOG.md` (screenshot-sourced inventory).
- **Do:** Inventory real Stratus C patterns → bring them out as screenshots → synthesize into `.c`/`.h` fixtures. **Deliberately include the hard patterns**: function pointers, macros, `#ifdef`, Stratus header/include idioms.
- **Acceptance:** the tree is a valid single-repo clone target; the hard patterns are present (they are what produce `coverage: coarse` + `unresolved_patterns` in §3.3).
- **Fixture / proof:** this task *is* the fixture for TASK-009/011/012/036.
- **Satisfies:** FR-DC-13, FR-DC-16, FR-DC-17.

### TASK-005 — Signed-off expected `code_map` (regression oracle)
- **Phase:** P1 · **Depends on:** TASK-004
- **Model:** Sonnet — careful JSON authoring per §3.3 schema; human must review and sign off (`fixtures/c_repo/`).
- **Reads:** `docs/TECH_SPEC.md` §3.3 (normative `code_map.json`); `docs/REQUIREMENTS.md` D5 (tag set).
- **Creates / edits:** `fixtures/c_repo/expected_code_map.json` + `fixtures/c_repo/SIGNOFF.md` (who/when).
- **Do:** Author the **human-signed-off** expected `code_map.json` for the TASK-004 fixtures — the regression set that defines "correct."
- **Acceptance:** conforms to §3.3 (`language`, both dependency directions, reserved `external_calls`/`exposes` empty, `coverage_report`); **sign-off is recorded** — the grader is NOT model-self-generated/self-graded.
- **Fixture / proof:** this *is* the grading oracle for TASK-012.
- **Satisfies:** FR-DC-14, FR-DC-10.

## Bucket 2 — Environment / tooling

### TASK-006 — C extractor tooling availability + fallback note
- **Phase:** P1 · **Depends on:** none. · **Toolchain:** `tree-sitter`/`tree-sitter-c` per **ADR-001** (was `ctags`/`cscope`).
- **Model:** Sonnet — check dep availability (venv import) + write a short note file
- **Reads:** `docs/design/ADR-001-c-extractor-tree-sitter.md`; `docs/TECH_SPEC.md` §5.2 (`tools_required`), §5.5/§5.7 (model-only fallback; port-time `port_check`).
- **Creates / edits:** `docs/ENV_PRECHECK.md` (availability results + provisioning/fallback decision per dep).
- **Do:** Confirm the C tooling (`tree-sitter` + `tree-sitter-c` importable in the venv); record provisioning or the model-only fallback where absent. Note this is a **port-time** check (§5.7), mirrored by the FR-XS-26 allow-list prerequisite.
- **Acceptance:** per dep — available → version; absent+provisionable → ops step (`pip install`); absent+unprovisionable → `enable_model_fallback(c)` applies (coarse coverage, never hard failure).
- **Fixture / proof:** `fixtures/c_repo/` (the extractor's first real target).
- **Satisfies:** FR-DC-14, FR-DC-17, NFR-04.

### TASK-007 — Copilot/VDI validation reference (PASSED — do not re-run)
- **Phase:** P1 · **Depends on:** none.
- **Model:** Sonnet — append a one-line note to an existing file; no reasoning needed
- **Reads:** `docs/COPILOT_VDI_VALIDATION.md` (runbook + result); `docs/REQUIREMENTS.md` D10 / FR-XS-24.
- **Creates / edits:** a one-line note in `docs/ENV_PRECHECK.md` citing the **PASSED 2026-06-16** outcome (no new artifact).
- **Do:** Record the dependency as **satisfied** — command execution + concurrent fan-out confirmed; org policy does not lock approval; allow-list home = **user scope** (FR-XS-26). **Do not re-run as a build task.**
- **Acceptance:** the note states PASSED + names the user-scope allow-list as a VDI prerequisite Generate surfaces (not scaffolder-emitted).
- **Fixture / proof:** n/a — already executed in the target VDI.
- **Satisfies:** FR-XS-22, FR-XS-23, FR-XS-24, FR-XS-26.

## Bucket 3 — Extractor onboarding (build + freeze the code-impact substrate)

> The whole bucket preserves: extractor **deterministic + frozen** (FR-DC-14), gate **model-free** (FR-DC-15), model owns **only `purpose`+`tags`** (FR-DC-17).

### TASK-008 — Language detection + partition + dispatcher (normalization contract)
- **Phase:** P1 · **Depends on:** none. · **Amended by ADR-002** (per-language partition dispatch).
- **Model:** Sonnet — Python dispatcher logic + skill markdown; clear spec in §5.5
- **Reads:** `docs/TECH_SPEC.md` §5.5 (the `dispatch()` pseudocode + normalization contract), §5.1 (terms), §3.3 (file-entry schema); `docs/design/ADR-002-polyglot-partition-dispatch.md`.
- **Creates / edits:** `core/skills/code_map_build.skill.md` (refine the seed `docs/code_map_build.skill.md`) — the dispatcher portion: `partition_by_language` → per partition `extractor_for(lang)` → `normalize` → `merge_edges`; and a thin `core/extractors/__init__.py` registration point.
- **Do:** Implement deterministic language detection (file-glob histogram + build-manifest signals), `partition_by_language` (ADR-002), and the dispatch skeleton that routes each language partition to its extractor and normalizes output to the §3.3 file-entry shape. `detect_language` retained for the dominant language (top-level + gate/cache key).
- **Acceptance:** `detect_language` / `partition_by_language` are deterministic (no model); the normalization contract maps any extractor's raw output to `path/module/interfaces/depends_on/used_by/coverage`; dispatcher has a slot for the C extractor (TASK-009) and the fallback (TASK-010).
- **Fixture / proof:** `fixtures/c_repo/` detects as `c`; `fixtures/mixed_repo/` partitions into `c` (majority) + python/java residue.
- **Satisfies:** FR-DC-15, FR-DC-17.

### TASK-009 — C extractor (tree-sitter → structural fields)
- **Phase:** P1 · **Depends on:** TASK-008 · **Toolchain:** `tree-sitter` + `tree-sitter-c` per **ADR-001**.
- **Model:** Sonnet — Python extractor using `tree-sitter-c` CST queries; clear input/output contract in §5.5 (dispatcher), TASK-004 (`fixtures/c_repo/`).
- **Reads:** `docs/design/ADR-001-c-extractor-tree-sitter.md`; `docs/design/ADR-002-polyglot-partition-dispatch.md` (extractor consumes a **file list**, not the whole repo); `docs/TECH_SPEC.md` §5.5 (extractor owns structural fields only), §3.3 (file-entry schema, `coverage_report`); `docs/REQUIREMENTS.md` FR-DC-17.
- **Creates / edits:** `core/extractors/c_extractor.py`; `register_extractor("c", …)` in `core/extractors/__init__.py`.
- **Do:** Accept the **C-language partition** (the `files` list the dispatcher passes per ADR-002, not a self-glob of the repo). Use `tree-sitter-c` to parse each file and pull **structural fields only** (`path/module/interfaces/depends_on/used_by`) and emit a `coverage_report`. **Exclude `static` file-local functions from `interfaces[]`.** Mark static-analysis blind spots (function pointers via `field_expression`/computed callees, macro-generated functions surfaced as `ERROR` nodes, `#ifdef`/vendor escapes) as `coverage: coarse` with `unresolved_patterns`.
- **Acceptance:** the extractor emits the structural fields per §3.3; it does **not** set `purpose`/`tags` (those are TASK-011); `merge_edges` (TASK-011) consumes its `depends_on`/`used_by`; **runs over the file list it is handed** (registered via `register_extractor`); output matches the TASK-005 oracle on `fixtures/c_repo`.
- **Fixture / proof:** runs over `fixtures/c_repo/` and produces structural entries for the easy files; flags the hard patterns.
- **Satisfies:** FR-DC-15, FR-DC-17.

### TASK-010 — Model fallback path (over a file set; whole-repo + residue)
- **Phase:** P1 · **Depends on:** TASK-008.
- **Model:** Sonnet — adding a fallback branch to an existing skill file; logic is clearly defined in §5.5 + ADR-002
- **Reads:** `docs/TECH_SPEC.md` §5.5 (`model_fallback`), §5.7 (safety net), §5.4 (`files_fallback` in `coverage_report`); `docs/design/ADR-002-polyglot-partition-dispatch.md`; `docs/REQUIREMENTS.md` FR-DC-17.
- **Creates / edits:** the fallback branch in `core/skills/code_map_build.skill.md`.
- **Do:** `model_fallback(files)` derives structure via the model over a **file set** and marks **all** its entries `coverage: coarse`. It is the route for any partition whose language has no registered extractor — whether that is the **whole repo** (no extractor for the dominant language) or the **residue** of a polyglot repo (ADR-002). Residue files count as `files_fallback` in the `coverage_report`; top-level coverage is forced coarse only when the *whole* repo went to fallback.
- **Acceptance:** fallback output is schema-valid (§3.3) and explicitly lower-coverage; it is reached for exactly the partitions where `extractor_for(lang)` is None; residue entries contribute to `files_fallback` so coverage reflects the deterministic share (§5.4).
- **Fixture / proof:** `fixtures/mixed_repo/` — the C partition routes to the extractor, the non-C **residue** routes to fallback marked coarse; a fully non-C fixture routes entirely to fallback with forced top-level coarse.
- **Satisfies:** FR-DC-17.

### TASK-011 — Model enrichment (`purpose`+`tags`) + `merge_edges` + vocab assert
- **Phase:** P1 · **Depends on:** TASK-009
- **Model:** Sonnet — enrichment step + deterministic merge logic; division of labor clearly pinned in §5.5, TASK-014 (vocabulary — author it first if not done; or stub-assert and re-check at TASK-021).
- **Reads:** `docs/TECH_SPEC.md` §5.5 (model owns `purpose`+`tags` only; `merge_edges` deterministic; `assert tags ⊆ domain_vocabulary`), §3.3; `docs/REQUIREMENTS.md` D5, FR-DC-17.
- **Creates / edits:** the enrichment + edge-merge steps in `core/skills/code_map_build.skill.md`.
- **Do:** For each extractor entry, the **model sets `purpose` and `tags` only**; assert `tags ⊆ vocabulary`; run deterministic `merge_edges` (match `depends_on ↔ used_by` for closure).
- **Acceptance:** model never sets structural fields or edges; `merge_edges` is deterministic; the vocab assertion fires on an out-of-vocab tag.
- **Fixture / proof:** enriched map over `fixtures/c_repo/` with tags drawn only from D5.
- **Satisfies:** FR-DC-17, FR-DC-09.
- **Extended by ADR-003 (FR-DC-21):** the enrichment **contract** in `code_map_build.skill.md` now states `model_enrich` returns a **third** value `uncovered_concepts[]` (concepts present in a file that no vocabulary tag covers) emitted in the same pass — the vocabulary-adequacy byproduct. It does **not** land on the map (`apply_enrichment` still writes only `purpose`+`tags`, unchanged); it routes to the ledger and is aggregated by TASK-013. This is a contract/prose refinement to the model step (the committed Python guard is untouched); it is what lets the adequacy detector catch a *partially*-uncovered file, not just an empty-tag one.

### TASK-012 — Validate vs oracle · freeze · `onboarding_manifest.yaml`
- **Phase:** P1 · **Depends on:** TASK-009
- **Model:** Sonnet — validation script + YAML manifest; human must approve the freeze commit, TASK-011, TASK-005 (oracle).
- **Reads:** `docs/TECH_SPEC.md` §5.2 (`onboarding_manifest.yaml` schema), §5.4 (coverage floor 0.80); `docs/REQUIREMENTS.md` FR-DC-14, FR-DC-16; `docs/design/ADR-003-agent-assisted-vocabulary.md` (the reserved `vocab_sha`/`adequacy_threshold` fields).
- **Creates / edits:** `core/onboarding_manifest.yaml`; freeze-commit `core/extractors/c_extractor.py`.
- **Do:** Validate extractor output against the **signed-off** `fixtures/c_repo/expected_code_map.json`; meet `coverage_floor`; **human-gate the freeze** and record the manifest (`extractor_sha`, `tools_required`, `file_globs`, `coverage_floor`, `frozen_at`, `frozen_by`). **Also reserve (ADR-003, behavior-free hook):** top-level `adequacy_threshold: 0.20` + `vocab_sha` (constant while the domain vocabulary is frozen), and `built_with_vocab_sha` on the repo entry — mirroring how `external_calls`/`exposes` were reserved so a later vocabulary amendment is additive, not a cache-key reshape. Per ADR-002, `coverage_report.files_seen` counts **all** source files in the repo and residue (non-extractor) files are `files_fallback`, so `coverage = files_extracted / files_seen` reflects the deterministic share — a genuinely polyglot repo trips the floor (→ TASK-013 `REONBOARD_FLAG`), while `fixtures/c_repo/` (single-language) is unaffected.
- **Acceptance:** output matches the oracle; `coverage ≥ 0.80` on `fixtures/c_repo/`; freeze is human-gated (model proposes, human commits); `extractor_sha` recorded; **reserved `adequacy_threshold` + `vocab_sha` (+ repo `built_with_vocab_sha`) present in the manifest** (constant; consumed by TASK-013).
- **Fixture / proof:** the signed-off oracle (TASK-005).
- **Satisfies:** FR-DC-14, FR-DC-16.

### TASK-013 — 3-branch gate (model-free) + re-onboard flag + L1 vocabulary-adequacy detector
- **Phase:** P1 · **Depends on:** TASK-012
- **Model:** Sonnet — gate algorithm is fully specified in §5.3; deterministic logic, no judgment calls (`onboarding_manifest.yaml`).
- **Reads:** `docs/TECH_SPEC.md` §5.3 (the 3-branch `GATE` algorithm — onboard / reuse / rebuild, now incl. the `vocab_sha` cache-key guard), §5.4 (coverage check) **and §5.4.1 (the L1 vocabulary-adequacy detector)**; §3.6 (`reonboard_flag` **+ `vocab_gap_flag`**); `docs/REQUIREMENTS.md` FR-DC-15, FR-DC-16, **FR-DC-21**; `docs/design/ADR-003-agent-assisted-vocabulary.md`.
- **Creates / edits:** the gate logic in `core/skills/code_map_build.skill.md`; a `reonboard_flag` writer into `decisions.jsonl`; **`core/scripts/checks/vocab_adequacy.py`** (the deterministic L1 detector) + a `vocab_gap_flag` writer.
- **Do:** Implement the gate using **only** deterministic signals (language detection, extractor presence, content hash, `extractor_sha`, **`vocab_sha`**). Branch A onboard / B reuse-cached / C rebuild-changed-files-only; coverage<floor → `REONBOARD_FLAG`. Per ADR-002, Branch A (onboard) is keyed on the **dominant** language (`detect_language`); an un-onboarded **residue** language is not its own branch — it is covered by fallback and surfaced through the coverage floor (`REONBOARD_FLAG` names the residue language). **Add `vocab_sha` to the Branch-B cache key** (a vocab amendment → re-tag; constant/inert while the vocabulary is frozen). **Add the L1 vocabulary-adequacy detector** (ADR-003 / §5.4.1): the deterministic aggregation of the `uncovered_concepts[]` the enrichment pass now emits (TASK-011) — a concept that **recurs** across the net-new delta → `VOCAB_GAP_FLAG(concept, evidence)` — **plus** a model-free `untagged_ratio` floor (entries with `tags == []`) raised against `adequacy_threshold`. The `uncovered_concepts` signal catches a *partially*-uncovered file (non-empty but with leftover meaning) that the empty-count floor would miss; the floor is the always-on safety net. Emit `untagged_ratio` as telemetry every run. The run is **not blocked** (advisory runtime flag; containment §10.1 stays the hard gate). The model **proposal**/amendment/re-tag half (L2) is **deferred** — not built here.
- **Acceptance:** **no model in the branch decision**; no-change → reuse; content change → `git_diff_names` rebuild of changed files only; the frozen extractor is **never** modified; a polyglot repo below floor raises `REONBOARD_FLAG` for the residue language (not a crash, not a silent drop). **The adequacy aggregation is deterministic; a recurring `uncovered_concepts` entry raises `VOCAB_GAP_FLAG` naming the concept, and the `untagged_ratio` floor fires iff `untagged_ratio > adequacy_threshold`; the run still completes and the vocabulary is never auto-grown.**
- **Fixture / proof:** `fixtures/c_repo/` at two commits (one no-op, one content change) + a coverage-floor-busting variant. **For L1:** `fixtures/c_repo/` enriched map (`uncovered_concepts` ≈ ∅, floor ≈0.06 → **no** flag) + a crafted variant — a *fully*-uncovered out-of-vocab file **and** a *partially*-uncovered one (carries `routing` plus a `tokenization` concept with no tag) → `uncovered_concepts` populates and `VOCAB_GAP_FLAG` fires for both (the partial case is the one an empty-count would miss) — the same proof shape as `assert_tags_in_vocabulary`.
- **Satisfies:** FR-DC-15, FR-DC-16, FR-DC-21.

## Bucket 4 — Domain seam (`payment_brand`)

> Registration is build-time: a domain exists iff its seam artifacts are present (§6.6.1). Key stays `payment_brand`; "PBI" is the UI label only. `jira_template` is **not** authored this slice.

### TASK-014 — `vocabulary.payment_brand.yaml` (transcribe D5)
- **Phase:** P1 · **Depends on:** none.
- **Model:** Sonnet — direct verbatim transcription of the D5 table; zero design decisions
- **Reads:** `docs/REQUIREMENTS.md` D5 (the 12-tag table + "emitted by" + code-tag flags); `docs/TECH_SPEC.md` §10.1.
- **Creates / edits:** `core/profiles/payment_brand/vocabulary.payment_brand.yaml`.
- **Do:** Transcribe the pinned D5 vocabulary verbatim — all 12 tags with the "emitted by" mapping preserved (it is the §10.5 cross-check target).
- **Acceptance:** 12 tags present; "emitted by" mapping verbatim; no tag added/renamed (would ripple D5).
- **Fixture / proof:** §10.1/§10.5 checks (TASK-021, TASK-046).
- **Satisfies:** FR-DC-08, FR-DC-09.

### TASK-015 — `brd_profile.payment_brand.yaml` (D1)
- **Phase:** P1 · **Depends on:** TASK-014.
- **Model:** Opus — every `must_capture` + `probe_if_missing` written here is the completeness contract for every BRD run; a weak probe or wrong topic here propagates to every session that writes a BRD
- **Reads:** `docs/REQUIREMENTS.md` D1 (normative section schema), FR-BR-10, D2 (baseline stays inline in author skill); `docs/TECH_SPEC.md` §6.1.
- **Creates / edits:** `core/profiles/payment_brand/brd_profile.payment_brand.yaml`.
- **Do:** Author per-section `sources` + `requirements{topic, must_capture, probe_if_missing, required}`; topics implicit from `requirements[].topic` (no `topics:` field). Route the code-impact section to `source: bitbucket` (drives FR-BR-07).
- **Acceptance:** every topic ∈ vocabulary; no standalone `topics:` field (FR-BR-10); section `id`s align with the inline baseline for deep-merge (D2).
- **Fixture / proof:** §10.1 (TASK-046).
- **Satisfies:** FR-BR-01, FR-BR-10, FR-DC-09.

### TASK-016 — `frd_profile.payment_brand.yaml` (D3a)
- **Phase:** P1 · **Depends on:** TASK-014, TASK-015.
- **Model:** Opus — same stakes as TASK-015 plus `traces_to` must resolve to real BRD anchors; bad traces break `frd_validator` traceability score at G2
- **Reads:** `docs/REQUIREMENTS.md` D3a (normative), FR-FR-06; `docs/TECH_SPEC.md` §9.3 (testability by `functional_kind`).
- **Creates / edits:** `core/profiles/payment_brand/frd_profile.payment_brand.yaml`.
- **Do:** BRD-profile shape + per-section `functional_kind` + per-topic mandatory `traces_to` (resolving to real BRD anchors in TASK-015's profile).
- **Acceptance:** every topic carries `traces_to`; `functional_kind ∈ {actor_flow|system_behavior|data_contract|error_state|nfr}`; topics ⊆ vocabulary.
- **Fixture / proof:** §10.1 (TASK-046); `frd_validator` traceability (TASK-045).
- **Satisfies:** FR-FR-01, FR-FR-06, FR-DC-09.

### TASK-017 — `adapter.yaml` + `pdf_extract` skill
- **Phase:** P1 · **Depends on:** TASK-014.
- **Model:** Sonnet — YAML pack manifest + one skill file; must surface F1 flag, not resolve it
- **Reads:** `docs/TECH_SPEC.md` §6.6.3 (normative `adapter.yaml` + the `payment_brand` instance, incl. `emits` per skill), §10.5; `docs/REQUIREMENTS.md` D5 "emitted by".
- **Creates / edits:** `core/profiles/payment_brand/adapter/adapter.yaml` + `.../adapter/pdf_extract.skill.md`.
- **Do:** Author the pack manifest (`docs_pipeline` ordered; `code_pipeline` → the shared `core/skills/code_map_build.skill.md`) and the `pdf_extract` skill (`emits: []` — structural extraction, no tags).
- **Acceptance:** `adapter.yaml` matches §6.6.3 emit-map; `pdf_extract.emits == []`. **Surface open flag F1** (the D5-vs-§6.6.3 `mandate` emitter mismatch) to V here — do not silently pick; §10.5 (TASK-021) is the gate.
- **Fixture / proof:** §10.5 (TASK-021).
- **Satisfies:** FR-DC-03, FR-DC-08, FR-DC-09.

### TASK-018 — `article_summarize` skill
- **Phase:** P1 · **Depends on:** TASK-017.
- **Model:** Sonnet — skill markdown authoring; emit tags are pinned by §6.6.3 and D5
- **Reads:** `docs/TECH_SPEC.md` §6.6.3 (`article_summarize.emits`); `docs/REQUIREMENTS.md` D5.
- **Creates / edits:** `core/profiles/payment_brand/adapter/article_summarize.skill.md`.
- **Do:** Author the doc-summarization skill emitting `[brand_rules, message_format, interchange_fees, reporting, mandate, transaction_flow]` (the F1/emit-map-reconciled set from TASK-017 — `+mandate, +transaction_flow` over §6.6.3's original example; see CLAUDE.md "Resolved flag").
- **Acceptance:** `emits` ⊆ vocabulary and matches the (reconciled) `adapter.yaml` map.
- **Fixture / proof:** §10.5 (TASK-021); TASK-003 PDF.
- **Satisfies:** FR-DC-03, FR-DC-09.

### TASK-019 — `change_type_assess` skill
- **Phase:** P1 · **Depends on:** TASK-017.
- **Model:** Sonnet — skill markdown authoring; emit tags are pinned by §6.6.3 and D5
- **Reads:** `docs/TECH_SPEC.md` §6.6.3 (`change_type_assess.emits`); `docs/REQUIREMENTS.md` D5.
- **Creates / edits:** `core/profiles/payment_brand/adapter/change_type_assess.skill.md`.
- **Do:** Author the classify/assess skill emitting `[mandate, card_brand, routing, certification, compliance_deadline]` (per §6.6.3; reconcile F1).
- **Acceptance:** `emits` ⊆ vocabulary and matches the `adapter.yaml` map.
- **Fixture / proof:** §10.5 (TASK-021); TASK-003 PDF.
- **Satisfies:** FR-DC-03, FR-DC-09.

### TASK-020 — Slice-1 connectors (`clone.py` + document/PDF source)
- **Phase:** P1 · **Depends on:** none.
- **Model:** Sonnet — two straightforward Python connector scripts; contract in §6.6.2
- **Reads:** `docs/TECH_SPEC.md` §6.6.2 (connector contract), §10.4; `docs/REQUIREMENTS.md` D7 (never branch on domain), FR-DC-02/11/12.
- **Creates / edits:** `core/scripts/clone.py` + the document/PDF source connector (`core/scripts/ingest_sharepoint.py` **or** a direct file-path source per §6.6.2).
- **Do:** Author only the **two** slice-1 connectors — generic, source-type-keyed. Code "ingest" = `git clone` by SEAL ID into `repo/`.
- **Acceptance:** each consumes `UI_INPUT.sources[]` of its `type` + auth via `auth_ref` (never inline, FR-DC-12); **neither branches on `domain`** (D7). Confluence + other types are deferred.
- **Fixture / proof:** §10.4 (TASK-021); TASK-003 PDF + TASK-004 repo as clone target.
- **Satisfies:** FR-DC-02, FR-DC-11, FR-DC-12.

### TASK-021 — Domain-seam build checks (§10.3/10.4/10.5) green
- **Phase:** P1 · **Depends on:** TASK-014..020
- **Model:** Sonnet — verification task; run checks per spec pseudocode + record pass/fail; build-check scripts from TASK-046/047/048 may not exist yet — if so, run the checks manually per the pseudocode and re-confirm via TASK-048.
- **Reads:** `docs/TECH_SPEC.md` §10.3 (domain artifact presence), §10.4 (connector coverage), §10.5 (adapter coverage + no-drift).
- **Creates / edits:** none (verification); records pass/fail.
- **Do:** Prove the seam is registered + consistent. §10.3 — required seam artifacts present (`jira_template` **excluded** this slice); §10.4 — every `UI_INPUT.sources[].type` has a non-domain-branching connector; §10.5 — `emits(adapter) ⊆ vocabulary`, every `required:true` topic has a producing skill, `adapter.yaml` emit-map == vocabulary "emitted by" (no drift, **F1 reconciled**), every adapter skill file exists.
- **Acceptance:** all three checks green.
- **Fixture / proof:** the seam artifacts themselves.
- **Satisfies:** FR-DC-09, FR-XS-01.

> 🔁 **Fresh-context safe before Phase 2.**

---

# Phase 2 — Core scaffold & runtime-tool seam

The plumbing + overlays the spine runs on. The frozen extractor (P1) ports unchanged (§5.7). Both overlays are thin, hand-authored (D9); the instruction file is the only generated piece (FR-XS-07).

### TASK-022 — Run-workspace layout + ledger init
- **Phase:** P2 · **Depends on:** TASK-000.
- **Model:** Sonnet — workspace template + JSON schema validators; schemas pinned in §2.2/§3.4/§3.5/§3.6
- **Reads:** `docs/TECH_SPEC.md` §2.2 (run-workspace tree), §3.4 (`telemetry.jsonl`), §3.5 (`run_state.json`), §3.6 (`decisions.jsonl`); `docs/REQUIREMENTS.md` FR-XS-05.
- **Creates / edits:** a run-workspace template under `runs/_template/` (`context_set/`, `repo/`, `prompts/`, `ledger/{telemetry.jsonl,run_state.json,decisions.jsonl}`) + JSON-schema validators for the three ledger files.
- **Do:** Establish the on-disk artifact contract and an empty valid ledger that real runs (Phase 3) copy from.
- **Acceptance:** durable state in files (FR-XS-05); ledger holds the run record, artifacts hold content, **no artifact content in the ledger**; `run_state.json` validates against §3.5 (`status ∈ {pending,running,done,failed}`).
- **Fixture / proof:** the three ledger validators.
- **Satisfies:** FR-XS-05, FR-XS-15.

### TASK-023 — `merge_manifest.py`
- **Phase:** P2 · **Depends on:** TASK-022.
- **Model:** Sonnet — deterministic Python fan-in script; output schema pinned in §3.2
- **Reads:** `docs/TECH_SPEC.md` §3.2 (`index.json` shape + `sources_status`); `docs/REQUIREMENTS.md` FR-DC-05, D8c, NFR-07.
- **Creates / edits:** `core/scripts/merge_manifest.py`.
- **Do:** Deterministic fan-in: assemble per-source slices into `index.json`; record failed sources in `sources_status` (never drop).
- **Acceptance:** same slices → identical `index.json`; a failed source is marked, not dropped (FR-DC-05/D8c); no authoring judgment (NFR-07).
- **Fixture / proof:** a two-source slice set + one deliberately-failed source.
- **Satisfies:** FR-DC-05, FR-XS-03, NFR-07.

### TASK-024 — `hydrate.py`
- **Phase:** P2 · **Depends on:** TASK-000.
- **Model:** Sonnet — git operations + file copy; mechanics pinned in Appendix B
- **Reads:** `docs/TECH_SPEC.md` Appendix B (hydration mechanics); `docs/REQUIREMENTS.md` FR-XS-10, NFR-01, NFR-07.
- **Creates / edits:** `core/scripts/hydrate.py`.
- **Do:** `git clone --depth 1` + `checkout <registry_sha>` + selective copy of `core/` + `profiles/<domain>/` + `templates/<domain>/` + `overlays/<tool>/` into a run scaffold. (In the external build the source is this repo; the mechanism is what ports.)
- **Acceptance:** re-hydrating one `registry_sha` reproduces the scaffold byte-for-byte (NFR-01); pure plumbing, no judgment (NFR-07).
- **Fixture / proof:** a fixed `registry_sha` hydrated twice.
- **Satisfies:** FR-XS-10, NFR-01, NFR-07.

### TASK-025 — `overlay_manifest.yaml` (D9)
- **Phase:** P2 · **Depends on:** none.
- **Model:** Sonnet — verbatim transcription of the D9 normative block; no decisions to make
- **Reads:** `docs/REQUIREMENTS.md` D9 / `docs/TECH_SPEC.md` §10.2 (the normative manifest block — 8 roles, 3 prompt files, per-tool launch).
- **Creates / edits:** `core/overlay_manifest.yaml`.
- **Do:** Transcribe the D9 block unchanged.
- **Acceptance:** 8 roles with `skill` + `user_invocable` (`brd_author`/`frd_author` true, workers false); `prompt_files: [start-brd, start-frd, start-jira]`; `claude`/`copilot` launch.
- **Fixture / proof:** §10.2 parity (TASK-047).
- **Satisfies:** FR-XS-20.

### TASK-026 — `instruction_file.template.md` + generation
- **Phase:** P2 · **Depends on:** TASK-025.
- **Model:** Sonnet — one canonical template + generation logic; placeholders pinned in §6.3
- **Reads:** `docs/TECH_SPEC.md` §6.3 (placeholders + single-template rule); `docs/REQUIREMENTS.md` FR-XS-07, NFR-02.
- **Creates / edits:** `core/instruction_file.template.md` + generation logic (used by TASK-031).
- **Do:** One canonical template; placeholders filled from `UI_INPUT` + `overlay_manifest` (`{{domain}} {{runtime_tool}} {{registry_sha}} {{run_id}} {{roles}} {{prompt_files}} {{stage_transition}} {{start_gesture}}`); emit exactly one of `CLAUDE.md` / `copilot-instructions.md` by `runtime_tool`.
- **Acceptance:** body identical across tools except the per-tool gesture/launch tail (NFR-02); **no runtime `AGENTS.md` pointer**.
- **Fixture / proof:** generate for `claude` and `copilot` from one `UI_INPUT.yaml`; diff = gesture/launch lines only.
- **Satisfies:** FR-XS-07, NFR-02.

### TASK-027 — Claude overlay: agent wrappers
- **Phase:** P2 · **Depends on:** TASK-025.
- **Model:** Sonnet — 8 thin wrapper files; each is a pointer to a shared skill, no logic
- **Reads:** `docs/TECH_SPEC.md` §6.2, §4 (wrapper = thin pointer to one shared skill); `docs/REQUIREMENTS.md` FR-XS-08, FR-XS-19.
- **Creates / edits:** `overlays/claude/.claude/agents/*.md` (8 wrappers).
- **Do:** Hand-author 8 thin wrappers, each body pointing at the one shared `core/skills/<role>`; frontmatter `user_invocable` per manifest.
- **Acceptance:** logic not copied (FR-XS-08); frontmatter matches `overlay_manifest.yaml`.
- **Fixture / proof:** §10.2 parity (TASK-047).
- **Satisfies:** FR-XS-08, FR-XS-19.

### TASK-028 — Claude overlay: prompt files + launch
- **Phase:** P2 · **Depends on:** TASK-027.
- **Model:** Sonnet — 3 prompt files + launch config; structure pinned in §6.4
- **Reads:** `docs/TECH_SPEC.md` §6.4 (stage transitions); `docs/REQUIREMENTS.md` FR-XS-11.
- **Creates / edits:** `overlays/claude/prompts/{start-brd,start-frd,start-jira}` + launch (`terminal_interactive`).
- **Do:** Author the three prompt files; each re-points a fresh agent at `UI_INPUT.yaml` + the prior artifact. Stage transitions are defined in the instruction file, **surfaced by the agent, performed by the operator** (`/clear`/new session) — agent never self-issues.
- **Acceptance:** three prompt files present; transition gesture is operator-performed (FR-XS-11).
- **Fixture / proof:** §10.2 parity (TASK-047).
- **Satisfies:** FR-XS-11, FR-XS-19.

### TASK-029 — Copilot overlay: agent wrappers
- **Phase:** P2 · **Depends on:** TASK-025
- **Model:** Sonnet — parity twin of TASK-027 in native Copilot syntax; mechanical; TASK-007 (VDI PASSED reference).
- **Reads:** `docs/TECH_SPEC.md` §6.2, §4; `docs/REQUIREMENTS.md` FR-XS-08, FR-XS-19, FR-XS-26.
- **Creates / edits:** `overlays/copilot/*.agent.md` (8 wrappers).
- **Do:** Parity twin of TASK-027 in native Copilot syntax (frontmatter + location differ; not abstracted), each pointing at the same shared skill.
- **Acceptance:** every manifest role present pointing at the correct shared skill; native syntax kept; the user-scope allow-list is a **VDI prerequisite Generate surfaces**, not scaffolder-emitted (FR-XS-26).
- **Fixture / proof:** §10.2 parity (TASK-047).
- **Satisfies:** FR-XS-08, FR-XS-19, FR-XS-26.

### TASK-030 — Copilot overlay: prompt files + launch
- **Phase:** P2 · **Depends on:** TASK-029.
- **Model:** Sonnet — parity twin of TASK-028 with Copilot-native gesture; mechanical
- **Reads:** `docs/TECH_SPEC.md` §6.4; `docs/REQUIREMENTS.md` FR-XS-11.
- **Creates / edits:** `overlays/copilot/prompts/{start-brd,start-frd,start-jira}` + launch (`agent_mode`).
- **Do:** Author the three prompt files; Copilot stage transition = `Ctrl+N` + prompt file (FR-XS-11).
- **Acceptance:** three prompt files present; transition operator-performed.
- **Fixture / proof:** §10.2 parity (TASK-047).
- **Satisfies:** FR-XS-11, FR-XS-19.

### TASK-031 — Scaffolder / Generate (two-step) + G0
- **Phase:** P2 · **Depends on:** TASK-024
- **Model:** Opus — central Generate script everything flows from; a logic error here means no run ever scaffolds correctly, TASK-026; TASK-002 (locked `UI_INPUT.yaml`).
- **Reads:** `docs/TECH_SPEC.md` §2.2, §6.3, Appendix B; `docs/REQUIREMENTS.md` FR-XS-03, FR-XS-09, D4 (G0).
- **Creates / edits:** `core/scripts/generate.py` (slice-1 scaffolder consuming the P0-locked `UI_INPUT.yaml`).
- **Do:** Deterministic Generate: lay the run workspace + generated instruction file + hydrated overlay, then **stop** for G0 inspection before run.
- **Acceptance:** Generate-scaffold and run are **two steps** (FR-XS-09); pure plumbing, no judgment (FR-XS-03); writes a `run_started` telemetry event.
- **Fixture / proof:** the P0 locked `UI_INPUT.yaml`; a G0 inspection checklist.
- **Satisfies:** FR-XS-03, FR-XS-09; D4/G0.

### TASK-032 — `telemetry.emit()` + ledger writers
- **Phase:** P2 · **Depends on:** TASK-022.
- **Model:** Sonnet — event envelope + per-event writers; schema pinned in §3.4/§8.1
- **Reads:** `docs/TECH_SPEC.md` §3.4, §8.1 (event table + `stage` vocabulary), §3.6; `docs/REQUIREMENTS.md` NFR-03, NFR-06, FR-MX-01.
- **Creates / edits:** `core/scripts/telemetry.py` (the `emit()` + `decisions.jsonl` writer + `run_state.json` updater).
- **Do:** Implement the envelope + per-event writers + gate/flag audit writer.
- **Acceptance:** every event carries the envelope (`ts, run_id, domain, tool, event`); payloads match §8.1; `stage` ∈ the §8.1 vocabulary; emissions suffice to compute all MVP metrics with no hand entry (NFR-06, FR-MX-01); gate/flag decisions record who/when/outcome/rationale (NFR-03).
- **Fixture / proof:** a synthetic event stream → `metrics_scan.py` (TASK-048) verifies derivations.
- **Satisfies:** FR-MX-01, NFR-03, NFR-06.

> 🔁 **Fresh-context safe before Phase 3.**

---

# Phase 3 — Framework build: the spine (first slice)

Each stage's output is the next stage's input, validated by fixtures. **BRD → FRD only** (no Jira).

## L1 — Ingestion

### TASK-033 — `source_processor` (fan-out, failure-isolated)
- **Phase:** P3 · **Depends on:** TASK-017, **TASK-023** (must emit the per-source slice that `merge_manifest.py` already consumes).
- **Model:** Opus — complex fan-out orchestration with failure isolation; this skill is the engine the entire ingestion pipeline runs on (`adapter.yaml`), TASK-022.
- **Reads:** `docs/TECH_SPEC.md` §4 (the `source_processor` rows); `docs/SKILLS_INDEX.md` (source_processor); `docs/REQUIREMENTS.md` FR-DC-01/05, D8b/c. **Also read the per-source slice contract in `core/scripts/merge_manifest.py`'s module docstring (defined at TASK-023; §3.2 pins only the `index.json` output, not this intermediate).**
- **Creates / edits:** `core/skills/source_processor.skill.md`.
- **Do:** One reusable fan-out worker; one instance per source in parallel; owns a source end-to-end and writes its slice + manifest entries. Reads `adapter.yaml` for run order; carries no domain knowledge itself.
- **⚠️ Slice contract — BINDING (the consumer `merge_manifest.py` already exists, TASK-023).** Each worker MUST write exactly one slice file at `context_set/<source>/_slice.json` with this shape; `merge_manifest.py` fans these in → `index.json`. Do not invent a different name/shape — change both sides together or the seam breaks (re-run `fixtures/merge_manifest` after any change).
  ```json
  {
    "source":  "<label>",                  // required — logical source label; partitions context_set/<source>/
    "status":  "ok" | "failed",            // required
    "domain":  "payment_brand",            // optional — carried up to index.json top level
    "files":   [ <§3.2 manifest entry>, … ],   // may be [] or PARTIAL on failure (D8c keeps partials)
    "note":    "code_map.json built",      // optional — e.g. the code arm builds no doc entries
    "reason":  "…"                          // required iff status=="failed" (the recorded gap, D8c)
  }
  ```
  Doc arm: `files[]` = the manifest entries the adapter pipeline built (`path/source/url/ingest_ts/adapter/change_type/topics/descriptor`). Code arm: typically `files: []` + `note`. A failed source still writes a slice (`status:"failed"` + `reason`) — never absent, never silently dropped (FR-DC-05/D8c). `merge_manifest.py` rejects a `failed` slice with no `reason`, a bad `status`, or non-list `files` as a loud error.
- **Acceptance:** split at the source/source-type boundary, **never per file** (FR-DC-05); a single source failing does **not** fail the batch — partials + gap list (D8c, FR-XS-18); each worker emits a contract-valid `_slice.json` that `merge_manifest.py` fans in cleanly (run the TASK-023 script over the live slices and confirm `index.json`).
- **Fixture / proof:** TASK-003 PDF + a deliberately-failing second source.
- **Satisfies:** FR-DC-01, FR-DC-05, FR-XS-18.

### TASK-034 — Document pipeline execution (extract→summarize→classify)
- **Phase:** P3 · **Depends on:** TASK-017/018/019
- **Model:** Sonnet — running the pipeline over fixtures and checking output against the oracle; execution not design (pack skills), TASK-033, TASK-003 (PDF + expected entries).
- **Reads:** `docs/TECH_SPEC.md` §3.2 (manifest entry shape + provenance tags), §3.2 routing rule; `docs/REQUIREMENTS.md` FR-DC-03/04/06.
- **Creates / edits:** run-workspace `context_set/<source>/*.md` + their `index.json` entries.
- **Do:** Run the PBI doc pipeline (`pdf_extract` → `article_summarize` → `change_type_assess`) over the PDF to produce provenance-tagged slices.
- **Acceptance:** emitted `topics` ⊆ vocabulary and match each producing skill's `emits` (§10.5); every entry provenance-tagged (FR-DC-04); selective-read routing works (`source ∈ section.sources AND topics ∩ section.topics ≠ ∅`).
- **Fixture / proof:** TASK-003 `expected_manifest_entries.json`.
- **Satisfies:** FR-DC-03, FR-DC-04, FR-DC-06.

### TASK-035 — Repo clone + `merge_manifest` → `index.json`
- **Phase:** P3 · **Depends on:** TASK-020
- **Model:** Sonnet — running clone + merge scripts; verifying deterministic output (`clone.py`), TASK-023 (`merge_manifest.py`), TASK-034.
- **Reads:** `docs/TECH_SPEC.md` §3.2; `docs/REQUIREMENTS.md` FR-DC-02/05, D8b.
- **Creates / edits:** run-workspace `repo/` (cloned at pinned `commit_sha`) + `context_set/index.json`.
- **Do:** Clone the SEAL-ID repo into `repo/`; assemble the merged `index.json` deterministically (with the bitbucket `sources_status` note).
- **Acceptance:** clone idempotent (skip if SHA-matching, D8b); `index.json` deterministic; failed sources marked.
- **Fixture / proof:** TASK-004 repo as clone target.
- **Satisfies:** FR-DC-02, FR-DC-05.

## L1 — Code map

### TASK-036 — `code_map_build` skill (frozen extractor + gate → `code_map.json`)
- **Phase:** P3 · **Depends on:** TASK-012
- **Model:** Sonnet — finalizing the skill and running the gate; all contracts already pinned in Phase 1 (frozen extractor + manifest), TASK-013 (gate), TASK-035 (`repo/`).
- **Reads:** `docs/TECH_SPEC.md` §3.3, §5.3, §5.5; `docs/REQUIREMENTS.md` FR-DC-10/14/15/17.
- **Creates / edits:** run-workspace `context_set/code_map.json` (cached by `commit_sha`); finalize `core/skills/code_map_build.skill.md`.
- **Do:** Drive the **frozen** extractor through the 3-branch gate to produce the coarse map.
- **Acceptance:** conforms to §3.3 (`language`, `built_with_extractor_sha`, both dep directions, `tags ⊆ vocabulary`, per-file + top-level coverage, `coverage_report`, reserved cross-repo fields empty); extractor never modified at runtime (FR-DC-14); gate model-free (FR-DC-15); model owns `purpose`+`tags` only (FR-DC-17); cache reused on no-change.
- **Fixture / proof:** TASK-005 oracle; TASK-004 repo at two commits.
- **Satisfies:** FR-DC-10, FR-DC-13, FR-DC-14, FR-DC-15, FR-DC-17.

## L2 — BRD

### TASK-037 — `brd_author`: baseline+profile merge + discovery
- **Phase:** P3 · **Depends on:** TASK-015
- **Model:** Opus — foundation of the BRD authoring skill; merge algorithm + discovery framing must be right before the section loop builds on it (`brd_profile`), TASK-034 (`index.json`), TASK-036 (`code_map.json`).
- **Reads:** `docs/brd_author.skill.md` (seed — baseline sections + operating procedure); `docs/REQUIREMENTS.md` D2 (inline baseline + merge algorithm), FR-BR-01/02; `docs/TECH_SPEC.md` §3.7 (BRD.md structure).
- **Creates / edits:** `core/skills/brd_author.skill.md` (merge + discovery portion).
- **Do:** Implement deterministic baseline+profile merge (by `id`, executive summary pinned last) and short framing discovery (load `UI_INPUT` + manifest, 2–3 questions, seed the coarse code pass).
- **Acceptance:** generic engine — no domain content hardcoded (FR-BR-01); merge per D2; discovery precedes section authoring (FR-BR-02); executive summary scheduled last.
- **Fixture / proof:** merge produces the expected ordered section plan from TASK-015's profile.
- **Satisfies:** FR-BR-01, FR-BR-02.

### TASK-038 — `brd_author`: section-by-section authoring loop
- **Phase:** P3 · **Depends on:** TASK-037.
- **Model:** Opus — the most complex part of the skill; selective-read routing + must_capture evaluation + probe logic + coverage footer all interlock here
- **Reads:** `docs/brd_author.skill.md` (per-section loop); `docs/REQUIREMENTS.md` FR-BR-03/04, NFR-05; `docs/TECH_SPEC.md` §3.2 (routing rule), §3.7 (coverage footer).
- **Creates / edits:** the per-section loop in `core/skills/brd_author.skill.md`; emits incremental `BRD.md` with per-section `<!-- coverage: {...} -->` footers.
- **Do:** For each section: select context by §3.2 routing, draft against `must_capture`, probe gaps (one topic at a time), mark coverage. **Always-selective read** — manifest always loaded, expand on demand, no load-all/threshold (FR-BR-04, NFR-05).
- **Acceptance:** information hierarchy source → frame → operator (FR-BR-03); selective routing per §3.2; coverage footer present per section.
- **Fixture / proof:** TASK-034 `context_set/` + TASK-036 `code_map.json`.
- **Satisfies:** FR-BR-03, FR-BR-04, NFR-05.

### TASK-039 — `brd_author`: cite-or-flag grounding + revisit/shared-memory
- **Phase:** P3 · **Depends on:** TASK-038.
- **Model:** Sonnet — grounding rules are clearly stated in FR-BR-05/06; no judgment calls in the implementation
- **Reads:** `docs/brd_author.skill.md` (grounding + revisiting rules); `docs/REQUIREMENTS.md` FR-BR-05/06; `docs/TECH_SPEC.md` §3.7.
- **Creates / edits:** the grounding + revisit rules in `core/skills/brd_author.skill.md`.
- **Do:** Every substantive claim cited inline (`[src: …]`/`[frame]`/`[operator]`) or `[TBD — unsourced]` — never invented (FR-BR-06); support revisiting earlier sections + shared memory (never re-ask; on mid-stage reset, persist facts first) (FR-BR-05).
- **Acceptance:** ungrounded items marked, not invented; answered questions never re-asked.
- **Fixture / proof:** a section with one unsourced `must_capture` (must mark `[TBD]`).
- **Satisfies:** FR-BR-05, FR-BR-06.

### TASK-040 — `code_impact`: coarse pass (map-only)
- **Phase:** P3 · **Depends on:** TASK-036
- **Model:** Sonnet — map-only read; match requirement topics × tags; clearly scoped in §5.6 (`code_map.json`).
- **Reads:** `docs/code_impact_assess.skill.md` (coarse mode); `docs/TECH_SPEC.md` §5.6; `docs/REQUIREMENTS.md` FR-BR-07.
- **Creates / edits:** `core/skills/code_impact_assess.skill.md` (coarse portion).
- **Do:** Coarse pass reads the **map only** (no source files): match requirement topics × map `tags`/`purpose` → ranked candidate areas to thread into early BRD sections.
- **Acceptance:** coarse mode reads no source files; output is candidate areas, not yet Flags.
- **Fixture / proof:** a requirement matched against TASK-005-shaped map tags.
- **Satisfies:** FR-BR-07.

### TASK-041 — `code_impact`: deep pass + required Flags
- **Phase:** P3 · **Depends on:** TASK-040
- **Model:** Opus — dependency closure reasoning across real source files; Flags schema every run; subtle correctness requirements (selective-read only the flagged slice; never decide scope), TASK-035 (`repo/`).
- **Reads:** `docs/code_impact_assess.skill.md` (deep mode + Flags); `docs/TECH_SPEC.md` §5.6, §3.6 (D6b Flags schema); `docs/REQUIREMENTS.md` FR-BR-12.
- **Creates / edits:** the deep pass + Flags output in `core/skills/code_impact_assess.skill.md`.
- **Do:** Deep pass selective-reads **only the flagged slice** from `repo/`, traces the real closure, and emits the **Flags** section every run (`type, area, finding, implication, options, recommended_option, severity, requirement_ref`); emit "no flags" when none. Recommends `severity`, never decides scope. BRD code-impact section stays business-framed (file/function detail → FRD).
- **Acceptance:** deep reads only the flagged slice; **Flags emitted every run** (FR-BR-12); never decides scope.
- **Fixture / proof:** a requirement that ripples beyond the obvious module (e.g. routing→settlement) against TASK-004/005.
- **Satisfies:** FR-BR-07, FR-BR-12.

### TASK-042 — `brd_author`: human-mediated flag loop + material threshold
- **Phase:** P3 · **Depends on:** TASK-039
- **Model:** Opus — material vs advisory threshold (D6c) + conditional re-run scoped to changed surface; getting this wrong either over-triggers expensive re-runs or under-triggers required ones, TASK-041, TASK-032 (ledger writers).
- **Reads:** `docs/REQUIREMENTS.md` D6c (material threshold), FR-BR-08/13; `docs/TECH_SPEC.md` §5.6, §9.5 (GF), §3.6.
- **Creates / edits:** the flag loop in `core/skills/brd_author.skill.md`; `decisions.jsonl` flag entries.
- **Do:** Surface → wait → apply → conditional-re-run. **No auto-applied scope changes** (FR-BR-08); flags one at a time with a recommendation; **material** (per D6c) → section revision + a `code_impact` re-run **scoped to the changed surface only** (FR-BR-13); otherwise advisory (no re-run); emit `flag_decision` telemetry.
- **Acceptance:** no auto scope change; material vs advisory handled per D6c; re-run scoped to changed surface.
- **Fixture / proof:** one material + one advisory scenario from TASK-041.
- **Satisfies:** FR-BR-08, FR-BR-13; D4/GF.

### TASK-043 — `brd_validator` + G1
- **Phase:** P3 · **Depends on:** TASK-042.
- **Model:** Sonnet — score formula is arithmetic; hard preconditions are clearly enumerated in §9.2
- **Reads:** `docs/TECH_SPEC.md` §9.2 (score formula + hard preconditions); `docs/REQUIREMENTS.md` FR-BR-09, FR-XS-13/14, D4.
- **Creates / edits:** `core/skills/brd_validator.skill.md` + G1 wiring + `validation`/`gate_decision` telemetry + `decisions.jsonl` gate entry.
- **Do:** Implement `brd_score = round(100*(0.7*topic_coverage + 0.3*citation_integrity))`; wire G1.
- **Acceptance:** **G1 passes iff** `score ≥ threshold (85)` **AND** (hard) every `required:true` topic satisfied/waived **AND** (hard) all flags resolved in `decisions.jsonl` (§9.2); validator is a soft-gate, never auto-advances (FR-XS-13); accept → BRD vN, reopen → vN+1 (FR-XS-14).
- **Fixture / proof:** a BRD with one unsatisfied required topic (must fail) + a complete one (must pass).
- **Satisfies:** FR-BR-09, FR-XS-13, FR-XS-14; D4/G1.

## L3 — FRD

### TASK-044 — `frd_author` (consume BRD vN; `traces_to`; detailed impact)
- **Phase:** P3 · **Depends on:** TASK-016
- **Model:** Opus — consumes accepted BRD and carries the detailed technical impact forward; traces_to must resolve correctly or G2 fails; complex skill (`frd_profile`), TASK-043 (accepted `BRD.md`), TASK-041 (deep impact).
- **Reads:** `docs/TECH_SPEC.md` §3.7 (FRD.md structure + traces block); `docs/REQUIREMENTS.md` FR-FR-01..04, FR-FR-06; `docs/SKILLS_INDEX.md` (frd_author).
- **Creates / edits:** `core/skills/frd_author.skill.md`; run-workspace `FRD.md`.
- **Do:** Drive FRD authoring off `frd_profile`, consuming accepted `BRD.md`; carry the **detailed technical code impact** forward (BRD stays business-framed); every FRD topic `traces_to` a real BRD anchor; inquiry mode + modify-via-chat with diff preview; pin to BRD vN.
- **Acceptance:** consumes accepted BRD (FR-FR-02); file/function detail in FRD (FR-FR-03); `traces_to` resolves (FR-FR-06); `<!-- pinned_brd: vN -->` present.
- **Fixture / proof:** accepted `BRD.md` from TASK-043 + TASK-041 deep detail.
- **Satisfies:** FR-FR-01..04, FR-FR-06.

### TASK-045 — `frd_validator` + G2
- **Phase:** P3 · **Depends on:** TASK-044.
- **Model:** Sonnet — score formula is arithmetic; traceability + testability rules clearly enumerated in §9.3
- **Reads:** `docs/TECH_SPEC.md` §9.3 (score + hard precondition); `docs/REQUIREMENTS.md` FR-FR-05, D4.
- **Creates / edits:** `core/skills/frd_validator.skill.md` + G2 wiring + telemetry + `decisions.jsonl` entry.
- **Do:** Implement `frd_score = round(100*(0.5*traceability + 0.5*testability))`; wire G2.
- **Acceptance:** **G2 passes iff** `score ≥ threshold` **AND** (hard) every BRD requirement traced or marked out-of-scope (§9.3); testability required for actor_flow/system_behavior/data_contract/error_state, measurable target for nfr; soft-gate.
- **Fixture / proof:** an FRD with one untraced BRD requirement (must fail) + a fully-traced one (must pass).
- **Satisfies:** FR-FR-05; D4/G2.

> 🔁 **Fresh-context safe before Phase 4.**

---

# Phase 4 — Build harness & acceptance

The five build checks become runnable, and the spine is exercised end-to-end on the fixtures.

### TASK-046 — §10.1 vocabulary containment check
- **Phase:** P4 · **Depends on:** TASK-014/015/016
- **Model:** Sonnet — Python assertion script; rule is a simple set-containment check (vocabulary + profiles).
- **Reads:** `docs/TECH_SPEC.md` §10.1 (the containment rule).
- **Creates / edits:** `core/scripts/checks/check_vocab_containment.py`.
- **Do:** Assert every topic referenced by `brd_profile`/`frd_profile` and every tag emitted by adapter skills ∈ `vocabulary.payment_brand.yaml`.
- **Acceptance:** passes on the real seam; fails on an injected out-of-vocab topic.
- **Fixture / proof:** an injected bad-topic profile variant.
- **Satisfies:** FR-DC-08, FR-DC-09.

### TASK-047 — §10.2 overlay parity check
- **Phase:** P4 · **Depends on:** TASK-025/027/028/029/030.
- **Model:** Sonnet — Python parity script; rule is manifest roles vs overlay files
- **Reads:** `docs/TECH_SPEC.md` §10.2 (parity rule); `docs/REQUIREMENTS.md` D9.
- **Creates / edits:** `core/scripts/checks/check_overlay_parity.py`.
- **Do:** Assert both overlays expose every `overlay_manifest` role pointing at the same shared skill, with the same 3 prompt files, differing only in tool-native syntax/launch.
- **Acceptance:** passes on real overlays; fails if a Copilot wrapper is missing or points at a divergent skill.
- **Fixture / proof:** a deleted-wrapper variant.
- **Satisfies:** FR-XS-08, FR-XS-19, FR-XS-20.

### TASK-048 — `build_checks.py` runner (all five) + `metrics_scan.py`
- **Phase:** P4 · **Depends on:** TASK-046
- **Model:** Sonnet — aggregating existing checks into one runner + metrics derivation from telemetry; mechanical, TASK-047; the §10.3/10.4/10.5 logic from TASK-021; TASK-032 (telemetry).
- **Reads:** `docs/TECH_SPEC.md` §10.1–§10.5 (all five checks), §8 (metrics derivations); `docs/REQUIREMENTS.md` FR-MX-01, NFR-06.
- **Creates / edits:** `core/scripts/build_checks.py` (runs all five, non-zero on any fail) + `core/scripts/metrics_scan.py` (derives MVP metrics from `telemetry.jsonl`).
- **Do:** Aggregate §10.1 (vocab) + §10.2 (parity) + §10.3 (domain artifacts) + §10.4 (connector coverage) + §10.5 (adapter coverage/no-drift) into one runner; build the read-only metrics scan.
- **Acceptance:** one command runs all five with clear pass/fail; **§10.5 reflects the F1 resolution**; `metrics_scan.py` derives every MVP metric from telemetry alone (no hand entry).
- **Fixture / proof:** the full seam (green) + each injected-failure variant (red); a synthetic telemetry stream.
- **Satisfies:** FR-DC-09, FR-XS-01, FR-XS-20, FR-MX-01, NFR-06.

### TASK-049 — Spine end-to-end acceptance (PDF + repo → BRD vN → FRD)
- **Phase:** P4 · **Depends on:** TASK-031
- **Model:** Opus — exercises the full spine including flag loop and gate reopens; highest-stakes task in the build; failure here means something in Phase 1–3 is wrong (Generate/G0) + all of Phase 3 + TASK-048.
- **Reads:** `docs/TECH_SPEC.md` §7 (end-to-end run narrative) + §9 (gates); `docs/REQUIREMENTS.md` FR-XS-09..14, D4.
- **Creates / edits:** `docs/ACCEPTANCE.md` (the run log + artifact links).
- **Do:** From the P0-locked `UI_INPUT.yaml`, run Generate→G0→ingestion→code_map→BRD/G1→FRD/G2 on TASK-003 PDF + TASK-004 repo. Exercise the flag loop and one G1 reopen→vN+1.
- **Acceptance:** clean `BRD.md` vN (passes G1: score + required topics + flags resolved) and an `FRD.md` pinned to it (passes G2: score + full traceability); `build_checks.py` green; ledger lets `metrics_scan.py` derive the run's metrics; **no Jira artifacts produced** (out of slice).
- **Fixture / proof:** TASK-003 + TASK-004 + the gate fixtures.
- **Satisfies:** FR-XS-09..14, FR-MX-01; D4 (G0/G1/G2/GF).

> 🔁 **External build complete at TASK-049.** The VDI-port artifact (thin overlay + `port_check` + allow-list runbook) is produced separately, off this validated repo.

---

# Phase 5 — Productionize + enhance

Two milestones, in order. **Milestone 5A is the priority:** stand up the UI and the live
source connectors so the operator can configure a run in the browser, hit **Generate**, then
open VS Code (Claude Code / Copilot) to drive BRD→FRD — a fresh end-to-end run, self-served.
The UI does **config + Generate only** (it writes `UI_INPUT.yaml` and runs `generate.py`; it
does **not** run the agent — auto-launch stays deferred). Two Bitbucket repos play distinct
roles: **repo #1 = the registry** (the selective PDLC folders Generate hydrates *from*),
**repo #2 = the C code source** entered in the UI as a `type: bitbucket` source (single
code-repo per run — cross-repo closure stays 5B). PDFs come from **SharePoint**. All
connectors + the auth seam are built **in this repo**; the UI writes the URLs/locations into
`UI_INPUT.yaml`. **Milestone 5B** is the enhancement backlog — tackled after 5A lands.

---

## Milestone 5A — Self-serve run (UI + hosted sources + live connectors)  *(PRIORITY)*

### TASK-050 — Generate backend service (FastAPI)
- **Phase:** P5-A · **Depends on:** TASK-031 (`generate.py`), TASK-048 (`build_checks.py`).
- **Model:** Sonnet — a service wrapper around an existing deterministic CLI; no new judgment.
- **Reads:** `docs/TECH_SPEC.md` §3.1 (UI_INPUT contract), §6.3 (instruction gen), Appendix B (hydrate); `core/scripts/generate.py` docstring.
- **Creates / edits:** `core/app/backend/` (FastAPI) — `POST /generate` (config → `UI_INPUT.yaml` → `generate.py` → G0 descriptor + checklist + scaffold path), `GET /runs/{id}/status` (reads `run_state.json` + `telemetry.jsonl`), `GET /runs/{id}/ui_input`.
- **Do:** Validate posted config against §3.1; write `UI_INPUT.yaml`; invoke `generate.py` (registry from config); return the G0 descriptor — **no agent run** (Generate only, FR-XS-09).
- **Acceptance:** valid config → `UI_INPUT.yaml` written + workspace scaffolded + G0 descriptor (`ran_workflow:false`); invalid config → 422 naming the failing field; status endpoint mirrors the ledger.
- **Fixture / proof:** replay `fixtures/UI_INPUT.example.yaml` fields through the API → byte-equal `UI_INPUT.yaml` + same descriptor as the CLI.
- **Satisfies:** FR-XS-02, FR-XS-09, FR-XS-16, NFR-01.

### TASK-051 — React Run Configurator (from `PDLC_Configurator.jsx`)
- **Phase:** P5-A · **Depends on:** TASK-050, TASK-002 (locked `UI_INPUT` contract), `docs/design/PDLC_Configurator.jsx`.
- **Model:** Sonnet — port a complete mockup to a working app; screens + `UI_INPUT` emit are already designed.
- **Reads:** `docs/design/PDLC_Configurator.jsx` (the 5 tabs + the `UI_INPUT` preview), `docs/TECH_SPEC.md` §3.1, `docs/REQUIREMENTS.md` FR-XS-06.
- **Creates / edits:** `core/app/frontend/` — the 5-tab configurator (IDE Repo Initializer · Domain · Project & Requirement · Artifact Inventory · Generator).
- **Do:** Realize the mockup as a working SPA. **Artifact Inventory** collects sources (SharePoint PDF URLs, Bitbucket code `repo_url`+`seal_id`, the registry location) → §3.1 `UI_INPUT.yaml`. **Generator** calls `POST /generate`, shows G0 + the **manual hand-off** steps (open VS Code Claude Code/Copilot; the UI does not start the agent).
- **Acceptance:** a non-technical operator completes all 5 tabs → Generate → workspace scaffolded; emitted `UI_INPUT.yaml` conforms to §3.1; the `runtime_tool` switch (claude|copilot) works (FR-XS-06); config immutable after Generate (re-config = new run).
- **Fixture / proof:** a click-through producing a `UI_INPUT.yaml` matching the example contract.
- **Satisfies:** FR-XS-02, FR-XS-06, FR-XS-16.

### TASK-052 — `jpmc_adapters` auth seam (real `resolve_auth`)
- **Phase:** P5-A · **Depends on:** TASK-000 (`jpmc_adapters/` dir); §7.
- **Model:** Sonnet — a bounded seam: map `auth_ref` → secret, no business logic.
- **Reads:** `docs/TECH_SPEC.md` §7 (auth/push seam); `docs/REQUIREMENTS.md` FR-DC-12.
- **Creates / edits:** `core/adapters/jpmc_adapters/auth.py` — `resolve_auth(auth_ref)` for `jpmc_adapters:bitbucket | :sharepoint | :confluence` → credentials from a pluggable secret backend (env/keyring now, JPMC store at port).
- **Do:** Replace the ambient-passthrough stub with a real resolver keyed by `auth_ref`; consumed by `clone.py` + `ingest_sharepoint.py`. Secret never inline, never in artifacts/ledger.
- **Acceptance:** `resolve_auth` returns usable creds per `auth_ref`; a missing secret fails loud (named); no secret reaches the workspace/ledger/artifacts (FR-DC-12); `auth_ref` recorded as a pointer only.
- **Fixture / proof:** a stub secret backend; resolve a bitbucket + a sharepoint `auth_ref`; assert no secret on disk.
- **Satisfies:** FR-DC-12, §7.

### TASK-053 — Registry (repo #1) on Bitbucket + hydrate-from-remote
- **Phase:** P5-A · **Depends on:** TASK-024 (`hydrate.py`), TASK-052, TASK-048 (publish gate).
- **Model:** Sonnet — packaging + remote-clone wiring on the existing hydrate path.
- **Reads:** `docs/TECH_SPEC.md` Appendix B (hydration), §2.1 (registry layout), §6.6.1.
- **Creates / edits:** a registry-publish manifest (the selective PDLC folders that constitute the registry — `core/`, `overlays/`, the `docs/` subset, profiles/templates) + remote-registry support in `hydrate.py`/`generate.py`.
- **Do:** Define the publishable registry subset and push it to Bitbucket as **repo #1**; make `--registry` accept a Bitbucket URL → clone at `registry_sha` through the auth seam → verify the SHA. Publish runs `build_checks.py` (§10) as a **hard gate** before push.
- **Acceptance:** `generate.py --registry <bitbucket-url>` hydrates at the pinned `registry_sha` on the **verified** path (not the non-git unverified convenience); a registry push is blocked unless build checks are green.
- **Fixture / proof:** hydrate from a local bare-git "Bitbucket" remote; `registry_sha_verified == requested`.
- **Satisfies:** FR-XS-10, NFR-01, §6.6.1.

### TASK-054 — Live Bitbucket code-source clone (repo #2)
- **Phase:** P5-A · **Depends on:** TASK-020 (`clone.py`), TASK-052.
- **Model:** Sonnet — validate the existing clone path against a real host + auth.
- **Reads:** `docs/TECH_SPEC.md` §6.6.2, §7; `docs/REQUIREMENTS.md` FR-DC-02/11/12.
- **Creates / edits:** `clone.py` auth wiring (resolve `auth_ref: jpmc_adapters:bitbucket` via TASK-052) — no contract change.
- **Do:** Clone the UI-supplied `repo_url` from a reachable Bitbucket host through the resolved auth seam into `repo/`; pin `commit_sha` (NFR-01); idempotent on SHA match (D8b).
- **Acceptance:** a real (or local-remote) Bitbucket repo clones end-to-end through the seam; `commit_sha` pinned + recorded; no secret on disk; §10.4 connector coverage stays green.
- **Fixture / proof:** clone from a local bare-git remote with a stub `auth_ref`.
- **Satisfies:** FR-DC-02, FR-DC-11, FR-DC-12, §7.

### TASK-055 — SharePoint PDF connector (`ingest_sharepoint.py`)
- **Phase:** P5-A · **Depends on:** TASK-020 (`ingest_file.py` contract), TASK-033 (`source_processor`), TASK-052.
- **Model:** Sonnet — one more source-type-keyed connector on the established contract.
- **Reads:** `core/scripts/ingest_file.py` (descriptor contract), `docs/TECH_SPEC.md` §6.6.2, §3.2; `docs/REQUIREMENTS.md` FR-DC-01/11/12.
- **Creates / edits:** `core/scripts/ingest_sharepoint.py`.
- **Do:** Pull a PDF from a SharePoint URL (auth via TASK-052) → stage under `context_set/<source>/` → emit the **same** source descriptor `pdf_extract` reads (identical shape to `ingest_file.py`). Never branches on `domain`.
- **Acceptance:** a SharePoint URL source stages the PDF + emits a contract-valid descriptor; downstream `pdf_extract → article_summarize → change_type_assess` unchanged; §10.4 maps `type:sharepoint → ingest_sharepoint.py` (green); no domain branch (AST check).
- **Fixture / proof:** a stub SharePoint endpoint serving the TASK-003 PDF; descriptor matches `ingest_file.py`'s shape.
- **Satisfies:** FR-DC-01, FR-DC-11, FR-DC-12.

### TASK-056 — Self-serve milestone acceptance (UI → Generate → tool → BRD/FRD)
- **Phase:** P5-A · **Depends on:** TASK-050..055.
- **Model:** Opus — the full operator-driven path; highest-stakes of 5A.
- **Reads:** `docs/ACCEPTANCE.md` (the TASK-049 spine run) + every 5A task above.
- **Creates / edits:** `docs/ACCEPTANCE_5A.md` (the self-serve run log + artifact links).
- **Do:** From the React UI, configure a run (Domain `payment_brand`; sources = SharePoint PDF(s) + Bitbucket code repo; registry = Bitbucket) → **Generate** (G0) → open VS Code Claude Code/Copilot in the scaffold → run the spine → accepted BRD + FRD. Nothing outside the seam changes.
- **Acceptance:** an operator completes a fresh run unaided through UI + tool; `UI_INPUT.yaml` carries the real URLs; sources pulled live through the connectors + auth seam; BRD/FRD pass G1/G2; `build_checks.py` green; `metrics_scan.py` derives the run's metrics.
- **Fixture / proof:** the run workspace + ledger + `docs/ACCEPTANCE_5A.md`.
- **Satisfies:** FR-XS-02/06/09/16, FR-DC-01/02/11/12.

> 🔁 **Milestone 5A done = self-serve run works.** Only then start Milestone 5B.

---

## Milestone 5B — Enhancements (backlog; decompose into tasks when 5A is done)

Each item is a future seam extension, not a gap — deferred by decision, not omission. Rough
priority order below. **Carried fixes (small, do alongside):** (a) `brd_validator.record_g1` /
`frd_validator.record_g2` hardcode `tool="claude"` in their telemetry `Emitter` regardless of
`UI_INPUT.runtime_tool` — thread the run's actual tool through (surfaced at TASK-049: the
acceptance ledger mixed `copilot`/`claude` envelopes). (b) Reconcile D5's `card_brand` /
`message_format` `emitted_by` gap in `docs/REQUIREMENTS.md` (the `vocabulary.yaml` r2 fix is
already in; D5 itself still carries it — port note). (c) `fixtures/UI_INPUT.example.yaml`
frame still says "Discover" while the bundled PDF fixture is the Mastercard mandate — align
for fixture consistency.

- **Jira push + `jpmc_adapters` + G3** — `jira_author`/`jira_validator` (§9.4), `jira_plan/` + `trace.json` (§3.8), the `jpmc_adapters` Jira interface (the **only** external mutation), gate G3, and `jira_template` in the seam (§10.3 will then require it). (FR-JR-*, FR-XS-17.)
- **Multi-input** — additional source connectors beyond 5A's SharePoint+Bitbucket: **Confluence** (`ingest_confluence.py`, in the §3.1 example) and other doc sources. Same source-type-keyed contract; `source_processor` already fans out. (SharePoint is promoted to 5A/TASK-055.)
- **Real JPMC host/secret validation (port-tied)** — 5A builds the auth seam (TASK-052) + clones through it from a local-remote Bitbucket (TASK-054) and pulls SharePoint from a stub (TASK-055). What remains is binding `auth_ref` to the **real JPMC secret store** and validating against the **live** Bitbucket/SharePoint servers — environment-specific, normally the **VDI-port** job. The mechanism is unchanged; only the secret backend + endpoints differ. (FR-DC-02/11/12, §7.)
- **Multi-repo** — populate the reserved `external_calls` / `exposes` cross-repo fields in `code_map.json` (§3.3) and cross-repo closure. (FR-DC-18.)
- **Fuller leverage of `purpose` in code_impact (enhances TASK-040/041; V-identified)** — today `purpose` (the model-owned free-text field on each `code_map` component) is used for *comprehension, ranking, and narrative grounding* but **not** for candidate *discovery*. Two additive enhancements, both deferred to the real (VDI) corpus where tagging is actually imperfect (our synthetic fixtures fit the 12 tags, so the value can't manifest in-slice):
  - **(1) `purpose`-as-discovery in the coarse pass (most valuable).** Today the coarse pass (TASK-040) matches requirement `topics` × code_map `tags` to pick candidate areas and uses `purpose` only to *rank* them. Enhancement: let the coarse pass — already a model-driven agent reading the map — also use `purpose` for **semantic candidate discovery** (surface a component whose `purpose` describes the requirement's concept even when the matching *tag* was not applied). Directly mitigates the **under-applied-existing-tag blind spot** (a mis-tagged file recoverable today only via deep-pass structural closure, and only if structurally connected). **Does not violate any binding rule** — the model-free constraint governs *building* the map (§5), not how the already-model-driven coarse consumer reasons over it; cost is a precision/recall tradeoff vs. the clean tag join, not architectural. Must stay advisory + cite-or-flag (never silently widen scope; surface via Flags).
  - **(2) Doc-side semantic-gap signal (closes ADR-005 open-Q #2).** The code side emits `uncovered_concepts` (leftover meaning the vocabulary lacks); the **document** side has `descriptor` but **no** equivalent. Add a doc-arm analog so vocabulary-adequacy detection (§5.4.1) is symmetric across both arms, not code-only.
  - *(Noted, lower value: `purpose` diffs between commits as a semantic-drift signal — the map cache key is structural `commit_sha`, so a same-structure/changed-behavior component re-tags identically today.)*
- **More language extractors + agent-assisted onboarding** — onboard Java/Python/etc. via the same gate; each frozen with its own `onboarding_manifest`. Adds the `extractor_onboard` skill (FR-DC-19): on Branch A it proposes/refines an extractor against a code sample and emits a reviewable enhancement artifact for human freeze. Not built this slice — C is onboarded manually (TASK-009/012); the model-only fallback (TASK-010) covers any unonboarded language meanwhile.
- **Vocabulary adequacy — L2 diagnosis + amendment loop (ADR-003 / FR-DC-21)** — the **L1 detector ships in-slice** (TASK-013): the deterministic `untagged_ratio` → `VOCAB_GAP_FLAG`. **Deferred to the port** is the model half: `vocab_gap_assess` (a bounded model pass over the *newly-introduced untagged* delta that proposes a candidate tag + evidence), the human-gated vocabulary **amendment**, the `vocab_sha` bump, and the re-tag pass. Its first meaningful exercise is the real (VDI) corpus — synthetic fixtures were authored to fit the 12 tags, so the gap cannot manifest here. The `vocab_sha` cache-key hook is reserved now (TASK-012/013), so the loop drops in additively.
- **Vocabulary onboarding for a new domain — `domain_onboard` (ADR-003 / FR-DC-20)** — propose a *new* domain's first `vocabulary.<domain>.yaml` from its sample docs + the **untagged** (`purpose`-only) code-map of a sample repo, as a reviewable artifact for human freeze (propose, never bless — the FR-DC-19 governance applied to the dictionary). Cannot be exercised until domain #2; `payment_brand`'s vocabulary is frozen by D5.
- **Profile integration — `profile_onboard` (ADR-004 / FR-DC-22)** — gate 3 of the adaptive-dictionary chain (detect → name a tag → **route it into a profile section**). When a vocabulary grows (FR-DC-20/21), a newly-approved tag is *taggable but unconsumed* until a profile section references it. The skill **surfaces** the unconsumed tag (FR-BR-08 surface→wait→apply loop), **proposes** a target section `id` + drafted `must_capture`/`probe_if_missing` (`sources` from the tag's `emitted_by`; `functional_kind`/`traces_to` for the FRD), and emits a **reviewable profile diff** — propose, never bless; the human approves and the change lands as a committed, re-pinned, build-time amendment (never a runtime mutation, §6.6.1). Runs in **two modes**: **bulk** (at onboarding, right after `domain_onboard` freezes the vocabulary — propose the whole first profile from vocab + baseline, refine + freeze in one session) and **incremental** (at drift — one new tag at a time). Vocabulary-first (§10.1 containment); onboarding order = `domain_onboard` → `profile_onboard` (bulk) → human refine/freeze. Deferred — at MVP the profiles are hand-authored (TASK-015/016) with no tag to integrate; first exercised alongside `domain_onboard`/the amendment loop.
- **Adapter onboarding — `adapter_onboard` (ADR-005 / FR-DC-23)** — the last domain-seam authoring aid (extractor/vocab/profiles already have one). A human-gated skill that, given a domain's **frozen** vocabulary + profiles + sample sources, **proposes the adapter pack by guided conversation**: shows the fixed frame (engine + fixed `code_pipeline → code_map_build`), designs the variable `docs_pipeline` (reuse shared/structural skills; scaffold net-new ad-hoc skills), and **derives each skill's `emits` from the vocabulary's `emitted_by`** so `adapter.yaml` cannot drift from the vocab by construction (kills the TASK-017 F1+3 drift class). Two modes: **bulk** (whole first pack right after `profile_onboard`) and **incremental** (one tag at drift). Propose-never-bless; references core skills, authors only domain pack skills, never `core/skills/`, never mutates at runtime. Onboarding order = `domain_onboard` → `profile_onboard` → **`adapter_onboard`** → human freeze. **Dependency:** promote `pdf_extract` (domain-agnostic structural) into `core/skills/` so it is available before the pack exists (tagging skills authored last). **Open Qs (ADR-005):** onboarding sample-input mechanism unspecified; doc-side vocab-adequacy detector missing. Deferred — at MVP the pack is hand-authored (TASK-017/018/019); first exercised at domain #2.
- **Domain-onboarding orchestrator — `onboard.py` + `ONBOARD_INPUT.yaml` (wraps FR-DC-19/20/22/23; answers ADR-005 open-Q #1)** — the four helper *skills* above (`extractor_onboard` → `domain_onboard` → `profile_onboard` → `adapter_onboard`) are the *proposers*; this is the **utility that sequences them end-to-end** so a new domain can be authored, frozen, and pushed back to the registry as one guided flow, after which a normal `mode: run` proceeds. **Design (V-proposed, to refine):**
  - **Config = a separate but `UI_INPUT`-shaped envelope with a `mode` discriminator** — `mode: onboard` (authors the registry) vs `mode: run` (consumes it). Deliberately **not** a flag bolted onto run-`UI_INPUT`: run config is the immutable consume-the-registry artifact (§3.1); onboarding carries different fields (`sample_sources[]` corpus, sample repo, `baseline`, the **new** `domain`) and a different output (a registry commit, not a run workspace). One shared schema style / UI affordance, two modes — this is the concrete answer to ADR-005's "sample-input mechanism unspecified (is it `UI_INPUT`-shaped?)".
  - **Flow:** `onboard.py` does the **authoring pull** (clone registry → `onboard_dir/` scratch), runs the four helpers **in the mandated order** with a **human freeze gate at each step** (propose → refine → freeze), then **runs `build_checks.py` (§10) as a HARD GATE** (containment §10.1, emit-map no-drift §10.5, coverage, parity §10.2) — **red ⇒ stop, no push** — then `git commit` + **push to Bitbucket**, and **emits the resulting `registry_sha`** to thread into the subsequent `mode: run` `UI_INPUT`.
  - **Governance (unchanged):** propose-never-bless throughout; the push is a **build-time developer `git` action**, not a runtime agent mutation (distinct from the run-time Jira push, the *only* external mutation of a run); the registry stays human-frozen + SHA-pinned (§6.6.1). Distinct from `hydrate.py` (TASK-024): that is the *consume* pull (copy a frozen SHA into a run); this is the *author* pull (edit the registry, push back).
  - **Depends on:** all four helper skills existing (FR-DC-19/20/22/23) + `build_checks.py` (TASK-048). First exercised at domain #2. Deferred — names the orchestration so the helpers land into a defined harness rather than ad-hoc invocation.
- **Multi-domain** — additional domain seams + `domains_index.yaml` (the `domain_onboard` flow above is its vocabulary-authoring aid); the YAML baseline extraction deferred under D2. (FR-BR-11/14, FR-XS-21 — all W.)
- **Metrics dashboard / SQLite** — promote the JSONL ledger to a queryable store + dashboard. (D8 persistence split; FR-MX-*.)
- **Auto-launch / Claude-only spine convenience** — operator-gesture automation beyond the two-step Generate.
- **FastAPI / React web UI** — **promoted to Milestone 5A (TASK-050 backend + TASK-051 frontend).** Remaining UI *enhancements* live here: role gating, a richer telemetry/metrics surface, and (separately) auto-launch (below).

---

# Build-and-port discipline (reminder)

This repo is the **external Claude Code build**. Do not add VDI/Copilot-air-gap accommodations into these tasks — the port is a separate, later artifact (thin overlay files + `port_check` per §5.7 + the user-scope allow-list runbook per FR-XS-26). Keep the core agent-agnostic; the runtime-tool seam is the only thing the port touches.

# Open flags (carry until resolved)

- **F1 — `mandate` emitter mismatch (unresolved).** `docs/REQUIREMENTS.md` D5 lists `mandate` emitted by **both** `change_type_assess` **and** `article_summarize`; `docs/TECH_SPEC.md` §6.6.3 `adapter.yaml` emits it **only** from `change_type_assess`. Surfaces at **TASK-017**, gated by **§10.5** at **TASK-021/048**. **Reconcile with V — do not pick.** Resolution must update whichever of D5 / §6.6.3 is wrong, then TASK-018/019 `emits` and the §10.5 no-drift check follow.
