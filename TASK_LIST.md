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
- [ ] TASK-004 — Synthetic Stratus C repo: payment routing code with function-pointer dispatch, macros, `#ifdef` patterns the extractor must handle · `Sonnet`
- [ ] TASK-005 — Hand-author `expected_code_map.json` against C fixtures; human-signed-off oracle that grades TASK-012 · `Sonnet`
- [ ] TASK-006 — Check `ctags`/`cscope` on PATH; write `ENV_PRECHECK.md` with version or fallback decision · `Sonnet`
- [ ] TASK-007 — Record Copilot/VDI PASSED 2026-06-16 note in `ENV_PRECHECK.md` (no re-run needed) · `Sonnet`
- [ ] TASK-008 — Language detection + dispatcher skeleton in `code_map_build.skill.md`; normalization contract maps any extractor output to §3.3 shape · `Sonnet`
- [ ] TASK-009 — C extractor: wrap `ctags`/`cscope` → structural fields only; mark function-pointer/macro/`#ifdef` blindspots as `coverage: coarse` · `Sonnet`
- [ ] TASK-010 — Model-only fallback branch: when no frozen extractor exists, derive structure via model, force all entries `coverage: coarse` · `Sonnet`
- [ ] TASK-011 — Model enrichment: model sets `purpose`+`tags` only; deterministic `merge_edges`; assert `tags ⊆ vocabulary` · `Sonnet`
- [ ] TASK-012 — Validate extractor output vs signed-off oracle; meet coverage floor 0.80; human-gate freeze; write `onboarding_manifest.yaml` · `Sonnet`
- [ ] TASK-013 — 3-branch gate (fully model-free): onboard / reuse-cached / rebuild-changed-files; `REONBOARD_FLAG` if below floor · `Sonnet`
- [ ] TASK-014 — Transcribe D5 vocabulary table verbatim into `vocabulary.payment_brand.yaml` (12 tags, emitted-by mapping) · `Sonnet`
- [ ] TASK-015 — Author `brd_profile.payment_brand.yaml`: `must_capture` + `probe_if_missing` per topic per section; foundation every BRD run depends on · `Opus`
- [ ] TASK-016 — Author `frd_profile.payment_brand.yaml`: same shape + `functional_kind` + `traces_to` resolving to real BRD anchors · `Opus`
- [ ] TASK-017 — `adapter.yaml` pack manifest + `pdf_extract` skill; surface open flag F1 (`mandate` emitter mismatch) to V · `Sonnet`
- [ ] TASK-018 — `article_summarize` skill: emits `brand_rules`, `message_format`, `interchange_fees`, `reporting` (reconcile F1) · `Sonnet`
- [ ] TASK-019 — `change_type_assess` skill: emits `mandate`, `card_brand`, `routing`, `certification`, `compliance_deadline` (reconcile F1) · `Sonnet`
- [ ] TASK-020 — Two generic source-type-keyed connectors: `clone.py` (Bitbucket) + `ingest_sharepoint.py` (or direct-file PDF) · `Sonnet`
- [ ] TASK-021 — Verify §10.3/10.4/10.5 domain-seam build checks all green; F1 reconciled before proceeding · `Sonnet`

**Phase 2 — Core scaffold & runtime-tool seam**
- [ ] TASK-022 — Run-workspace template under `runs/_template/` + JSON-schema validators for 3 ledger files · `Sonnet`
- [ ] TASK-023 — `merge_manifest.py`: deterministic fan-in of per-source slices → `index.json`; failed sources marked, never dropped · `Sonnet`
- [ ] TASK-024 — `hydrate.py`: `git clone` + checkout `registry_sha` + selective copy of `core/`+`profiles/`+`overlays/` into run scaffold · `Sonnet`
- [ ] TASK-025 — Transcribe D9 block into `overlay_manifest.yaml`: 8 roles, 3 prompt files, per-tool launch · `Sonnet`
- [ ] TASK-026 — One canonical `instruction_file.template.md`; generation emits `CLAUDE.md` or `copilot-instructions.md` by `runtime_tool` · `Sonnet`
- [ ] TASK-027 — Claude overlay: 8 thin `.md` agent wrappers, each body pointing at one shared `core/skills/` skill · `Sonnet`
- [ ] TASK-028 — Claude overlay: 3 prompt files (`start-brd/frd/jira`) + `terminal_interactive` launch · `Sonnet`
- [ ] TASK-029 — Copilot overlay: parity twin of TASK-027 in native Copilot syntax (frontmatter + location differ) · `Sonnet`
- [ ] TASK-030 — Copilot overlay: parity twin of TASK-028 with `agent_mode` launch + `Ctrl+N` gesture · `Sonnet`
- [ ] TASK-031 — `generate.py` scaffolder: deterministic Generate → run workspace + instruction file + G0 inspection checkpoint · `Opus`
- [ ] TASK-032 — `telemetry.py`: `emit()` + `decisions.jsonl` writer + `run_state.json` updater covering all §8.1 events · `Sonnet`

**Phase 3 — Framework build: the spine**
- [ ] TASK-033 — `source_processor` skill: fan-out worker per source; failure-isolated; reads `adapter.yaml` for run order; no domain knowledge · `Opus`
- [ ] TASK-034 — Run `pdf_extract`→`article_summarize`→`change_type_assess` over PDF fixtures; verify entries vs `expected_manifest_entries.json` · `Sonnet`
- [ ] TASK-035 — Clone SEAL-ID repo + run `merge_manifest.py` → assembled `index.json` with `sources_status` · `Sonnet`
- [ ] TASK-036 — `code_map_build` skill: drive frozen extractor through 3-branch gate → `code_map.json` per §3.3 · `Sonnet`
- [ ] TASK-037 — `brd_author`: deterministic baseline+profile merge + discovery framing (2–3 questions, seed coarse code pass) · `Opus`
- [ ] TASK-038 — `brd_author`: per-section authoring loop; §3.2 selective-read routing; `must_capture` check; probe gaps; coverage footer · `Opus`
- [ ] TASK-039 — `brd_author`: cite-or-flag grounding rules; revisit/shared-memory (never re-ask answered questions) · `Sonnet`
- [ ] TASK-040 — `code_impact` coarse pass: map-only, no source files; match requirement topics × `code_map` tags → ranked candidate areas · `Sonnet`
- [ ] TASK-041 — `code_impact` deep pass: selective-read flagged slice from `repo/`; trace real closure; emit Flags schema every run · `Opus`
- [ ] TASK-042 — `brd_author` flag loop: surface→wait→apply→conditional re-run; material vs advisory per D6c; no auto scope changes · `Opus`
- [ ] TASK-043 — `brd_validator` + G1: score = 0.7×topic_coverage + 0.3×citation_integrity; hard preconditions on required topics + flags · `Sonnet`
- [ ] TASK-044 — `frd_author` skill: consume accepted BRD; `traces_to`; carry file/function detail forward that BRD stays silent on · `Opus`
- [ ] TASK-045 — `frd_validator` + G2: score = 0.5×traceability + 0.5×testability; hard precondition every BRD requirement traced · `Sonnet`

**Phase 4 — Build harness & acceptance**
- [ ] TASK-046 — `check_vocab_containment.py`: assert all profile topics + adapter tags ∈ `vocabulary.payment_brand.yaml` · `Sonnet`
- [ ] TASK-047 — `check_overlay_parity.py`: both overlays expose all 8 manifest roles pointing at same shared skills · `Sonnet`
- [ ] TASK-048 — `build_checks.py` runner (all five checks) + `metrics_scan.py` deriving all MVP metrics from `telemetry.jsonl` · `Sonnet`
- [ ] TASK-049 — End-to-end acceptance: PDF + repo → BRD vN → FRD; flag loop + G1 reopen; `build_checks.py` green · `Opus`

**Phase 5 — Deferred follow-on (named only; see end of file)**

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

### TASK-006 — `ctags`/`cscope` availability + fallback note
- **Phase:** P1 · **Depends on:** none.
- **Model:** Sonnet — shell commands to check tool presence + write a short note file
- **Reads:** `docs/TECH_SPEC.md` §5.2 (`tools_required: [ctags, cscope]`), §5.5/§5.7 (model-only fallback; port-time `port_check`).
- **Creates / edits:** `docs/ENV_PRECHECK.md` (PATH results + provisioning/fallback decision per tool).
- **Do:** Confirm the C tooling; record provisioning or the model-only fallback where absent. Note this is a **port-time** check (§5.7), mirrored by the FR-XS-26 allow-list prerequisite.
- **Acceptance:** per tool — present → version; absent+provisionable → ops step; absent+unprovisionable → `enable_model_fallback(c)` applies (coarse coverage, never hard failure).
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

### TASK-008 — Language detection + dispatcher (normalization contract)
- **Phase:** P1 · **Depends on:** none.
- **Model:** Sonnet — Python dispatcher logic + skill markdown; clear spec in §5.5
- **Reads:** `docs/TECH_SPEC.md` §5.5 (the `dispatch()` pseudocode + normalization contract), §5.1 (terms), §3.3 (file-entry schema).
- **Creates / edits:** `core/skills/code_map_build.skill.md` (refine the seed `docs/code_map_build.skill.md`) — the dispatcher portion: `detect_language` → `extractor_for(L)` → `normalize` → `merge_edges`; and a thin `core/extractors/__init__` registration point.
- **Do:** Implement deterministic language detection (file-glob histogram + build-manifest signals) and the dispatch skeleton that routes to a per-language extractor and normalizes its output to the §3.3 file-entry shape.
- **Acceptance:** `detect_language` is deterministic (no model); the normalization contract maps any extractor's raw output to `path/module/interfaces/depends_on/used_by/coverage`; dispatcher has a slot for the C extractor (TASK-009) and the fallback (TASK-010).
- **Fixture / proof:** `fixtures/c_repo/` detects as `c`.
- **Satisfies:** FR-DC-15, FR-DC-17.

### TASK-009 — C extractor (ctags/cscope → structural fields)
- **Phase:** P1 · **Depends on:** TASK-008
- **Model:** Sonnet — Python wrapper around ctags/cscope; clear input/output contract in §5.5 (dispatcher), TASK-004 (`fixtures/c_repo/`).
- **Reads:** `docs/TECH_SPEC.md` §5.5 (extractor owns structural fields only), §3.3 (file-entry schema, `coverage_report`); `docs/REQUIREMENTS.md` FR-DC-17.
- **Creates / edits:** `core/extractors/c_extractor.py` (+ tool shims).
- **Do:** Wrap `ctags`/`cscope` to pull **structural fields only** (`path/module/interfaces/depends_on/used_by`) and emit a `coverage_report`. Mark static-analysis blind spots (function pointers/macros/`#ifdef`) as `coverage: coarse` with `unresolved_patterns`.
- **Acceptance:** the extractor emits the structural fields per §3.3; it does **not** set `purpose`/`tags` (those are TASK-011); `merge_edges` (TASK-011) consumes its `depends_on`/`used_by`.
- **Fixture / proof:** runs over `fixtures/c_repo/` and produces structural entries for the easy files; flags the hard patterns.
- **Satisfies:** FR-DC-15, FR-DC-17.

### TASK-010 — Model-only fallback path
- **Phase:** P1 · **Depends on:** TASK-008.
- **Model:** Sonnet — adding a fallback branch to an existing skill file; logic is clearly defined in §5.5
- **Reads:** `docs/TECH_SPEC.md` §5.5 (`model_fallback`), §5.7 (safety net); `docs/REQUIREMENTS.md` FR-DC-17.
- **Creates / edits:** the fallback branch in `core/skills/code_map_build.skill.md`.
- **Do:** When no frozen extractor exists for a language, derive structure via the model and mark **all** entries `coverage: coarse` + force top-level coverage coarse.
- **Acceptance:** fallback output is schema-valid (§3.3) and explicitly lower-coverage; it is only reached when `extractor_for(L)` is None.
- **Fixture / proof:** a non-C fixture file routes to fallback and is marked coarse.
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

### TASK-012 — Validate vs oracle · freeze · `onboarding_manifest.yaml`
- **Phase:** P1 · **Depends on:** TASK-009
- **Model:** Sonnet — validation script + YAML manifest; human must approve the freeze commit, TASK-011, TASK-005 (oracle).
- **Reads:** `docs/TECH_SPEC.md` §5.2 (`onboarding_manifest.yaml` schema), §5.4 (coverage floor 0.80); `docs/REQUIREMENTS.md` FR-DC-14, FR-DC-16.
- **Creates / edits:** `core/onboarding_manifest.yaml`; freeze-commit `core/extractors/c_extractor.py`.
- **Do:** Validate extractor output against the **signed-off** `fixtures/c_repo/expected_code_map.json`; meet `coverage_floor`; **human-gate the freeze** and record the manifest (`extractor_sha`, `tools_required`, `file_globs`, `coverage_floor`, `frozen_at`, `frozen_by`).
- **Acceptance:** output matches the oracle; `coverage ≥ 0.80`; freeze is human-gated (model proposes, human commits); `extractor_sha` recorded.
- **Fixture / proof:** the signed-off oracle (TASK-005).
- **Satisfies:** FR-DC-14, FR-DC-16.

### TASK-013 — 3-branch gate (model-free) + re-onboard flag
- **Phase:** P1 · **Depends on:** TASK-012
- **Model:** Sonnet — gate algorithm is fully specified in §5.3; deterministic logic, no judgment calls (`onboarding_manifest.yaml`).
- **Reads:** `docs/TECH_SPEC.md` §5.3 (the 3-branch `GATE` algorithm — onboard / reuse / rebuild), §5.4 (coverage check); §3.6 (`reonboard_flag`); `docs/REQUIREMENTS.md` FR-DC-15, FR-DC-16.
- **Creates / edits:** the gate logic in `core/skills/code_map_build.skill.md`; a `reonboard_flag` writer into `decisions.jsonl`.
- **Do:** Implement the gate using **only** deterministic signals (language detection, extractor presence, content hash, `extractor_sha`). Branch A onboard / B reuse-cached / C rebuild-changed-files-only; coverage<floor → `REONBOARD_FLAG`.
- **Acceptance:** **no model in the branch decision**; no-change → reuse; content change → `git_diff_names` rebuild of changed files only; the frozen extractor is **never** modified.
- **Fixture / proof:** `fixtures/c_repo/` at two commits (one no-op, one content change) + a coverage-floor-busting variant.
- **Satisfies:** FR-DC-15, FR-DC-16.

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
- **Do:** Author the doc-summarization skill emitting `[brand_rules, message_format, interchange_fees, reporting]` (per §6.6.3; reconcile against F1 outcome).
- **Acceptance:** `emits` ⊆ vocabulary and matches the (F1-reconciled) `adapter.yaml` map.
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
- **Phase:** P3 · **Depends on:** TASK-017
- **Model:** Opus — complex fan-out orchestration with failure isolation; this skill is the engine the entire ingestion pipeline runs on (`adapter.yaml`), TASK-022.
- **Reads:** `docs/TECH_SPEC.md` §4 (the `source_processor` rows); `docs/SKILLS_INDEX.md` (source_processor); `docs/REQUIREMENTS.md` FR-DC-01/05, D8b/c.
- **Creates / edits:** `core/skills/source_processor.skill.md`.
- **Do:** One reusable fan-out worker; one instance per source in parallel; owns a source end-to-end and writes its slice + manifest entries. Reads `adapter.yaml` for run order; carries no domain knowledge itself.
- **Acceptance:** split at the source/source-type boundary, **never per file** (FR-DC-05); a single source failing does **not** fail the batch — partials + gap list (D8c, FR-XS-18).
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

# Phase 5 — Deferred follow-on (named only — do NOT build this slice)

Each item is a future seam extension, not a gap. They are deferred by decision, not omission.

- **Jira push + `jpmc_adapters` + G3** — `jira_author`/`jira_validator` (§9.4), `jira_plan/` + `trace.json` (§3.8), the `jpmc_adapters` Jira interface (the **only** external mutation), gate G3, and `jira_template` in the seam (§10.3 will then require it). (FR-JR-*, FR-XS-17.)
- **Multi-input** — additional source connectors (Confluence/SharePoint variants) beyond the slice-1 two; `source_processor` already fans out.
- **Multi-repo** — populate the reserved `external_calls` / `exposes` cross-repo fields in `code_map.json` (§3.3) and cross-repo closure. (FR-DC-18.)
- **More language extractors** — onboard Java/Python/etc. via the same gate; each frozen with its own `onboarding_manifest`.
- **Multi-domain** — additional domain seams + `domains_index.yaml`; the YAML baseline extraction deferred under D2. (FR-BR-11/14, FR-XS-21 — all W.)
- **Metrics dashboard / SQLite** — promote the JSONL ledger to a queryable store + dashboard. (D8 persistence split; FR-MX-*.)
- **Auto-launch / Claude-only spine convenience** — operator-gesture automation beyond the two-step Generate.
- **FastAPI / React web UI** — implement Generate behind the P0-locked `UI_INPUT.yaml` contract for non-technical operators + role gating + telemetry surface.

---

# Build-and-port discipline (reminder)

This repo is the **external Claude Code build**. Do not add VDI/Copilot-air-gap accommodations into these tasks — the port is a separate, later artifact (thin overlay files + `port_check` per §5.7 + the user-scope allow-list runbook per FR-XS-26). Keep the core agent-agnostic; the runtime-tool seam is the only thing the port touches.

# Open flags (carry until resolved)

- **F1 — `mandate` emitter mismatch (unresolved).** `docs/REQUIREMENTS.md` D5 lists `mandate` emitted by **both** `change_type_assess` **and** `article_summarize`; `docs/TECH_SPEC.md` §6.6.3 `adapter.yaml` emits it **only** from `change_type_assess`. Surfaces at **TASK-017**, gated by **§10.5** at **TASK-021/048**. **Reconcile with V — do not pick.** Resolution must update whichever of D5 / §6.6.3 is wrong, then TASK-018/019 `emits` and the §10.5 no-drift check follow.
